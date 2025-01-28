BUFFER_SIZE = 1048576  # the file size is limited to 1 mb
DH_G = 5               # co-prime
DH_KEY_SIZE = 256      # bytes
DH_NONCE_SIZE = 16     # bytes
AES_KEY_SIZE = 32      # bytes

import os, socket, json

from Crypto.Util import number
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from OpenSSL import crypto

# =============================================
# ========= write your code below  ============
# =============================================

# the argument config contains all information passed to the command line
# you should explore what stores in it
# and use it to store anything you need between the different handlers
def send_client_hello(sock, config):
    # create and send client_hello payload
    nonce = get_random_bytes(DH_NONCE_SIZE)
    p=number.getStrongPrime(2048, e=DH_G)
    a=number.getRandomInteger(2048)
    DhA=pow(DH_G, a,p)
    p=p.to_bytes(DH_KEY_SIZE, byteorder='big')
    DhA=DhA.to_bytes(DH_KEY_SIZE, byteorder='big')
    payload = p+DhA+nonce
    sock.sendall(payload)
    config['nonce'] = nonce
    config['a'] = a
    config['p'] = p
    config['DhA'] = DhA

def receive_server_hello(sock, config):
    # receive and decode server_hello payload
    try:
        payload = sock.recv(BUFFER_SIZE)
        DhB=payload[:DH_KEY_SIZE]
        nonce=payload[DH_KEY_SIZE:DH_KEY_SIZE+DH_NONCE_SIZE]
        DhB_int=int.from_bytes(DhB, byteorder='big')
        p=int.from_bytes(config['p'], byteorder='big')
        master_key=pow(DhB_int,config['a'],p)
        session_k=HKDF(master_key.to_bytes(DH_KEY_SIZE,'big'),32,config['nonce']+nonce,SHA256,1)
        config['m']=master_key
        config['k']=session_k
        encrypted=payload[DH_KEY_SIZE+DH_NONCE_SIZE:]
        nonce1=encrypted[:DH_NONCE_SIZE]
        MAC=encrypted[DH_NONCE_SIZE:2*DH_NONCE_SIZE]
        ciphertext=encrypted[2*DH_NONCE_SIZE:]
        cipher=AES.new(config['k'], AES.MODE_GCM,nonce1)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, MAC)
        except (ValueError, KeyError):
            print("Incorrect decryption")
            sock.close()
            sys.exit(1)
        certB = plaintext[512:]
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, certB)

        # Assuming the certificates are in PEM format in a trusted_certs list
        try:
            store = crypto.X509Store()
            for _cert in config['roots']:
                client_certificate = crypto.load_certificate(crypto.FILETYPE_PEM, _cert)
                store.add_cert(client_certificate)
            # Create a certificate context using the store and the downloaded certificate
            store_ctx = crypto.X509StoreContext(store, certificate)
            # Verify the certificate, returns None if it can validate the certificate
           
        except Exception as e:
            print(e)
            sock.close()
            sys.exit(1)
        organization=certificate.get_subject().O
        # key = RSA.import_key(open('private_key.der').read())
        message=config['nonce']+nonce+config['DhA']+DhB+certB
        h=SHA256.new(message)
       
        public_key = RSA.import_key(crypto.dump_publickey(crypto.FILETYPE_PEM, certificate.get_pubkey()))
        pkcs1_15.new(public_key).verify(h, plaintext[:512])
        if  organization != 'bob' or  store_ctx.verify_certificate()  is not None:
            sock.close()
            sys.exit(1)

    except (ValueError, TypeError):
            sock.close()
            sys.exit(1)


def send_request(sock, config):
    # create and send request payload
    payload = json.dumps({'request': config['request'], 'filename': config['filename'], 'from': config['from']})
    cipher=AES.new(config['k'], mode=AES.MODE_GCM)
    ciphertext, MAC = cipher.encrypt_and_digest(payload.encode('utf-8'))
    sock.sendall((cipher.nonce+MAC+ciphertext))


def receive_ready(sock, config):
    # receive data from client
    data = sock.recv(BUFFER_SIZE)
    nonce=data[:DH_NONCE_SIZE]
    MAC=data[DH_NONCE_SIZE:2*DH_NONCE_SIZE]
    ciphertext=data[2*DH_NONCE_SIZE:]
    
    cipher=AES.new(config['k'], AES.MODE_GCM,nonce)
    try:
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, MAC)
        except (ValueError, KeyError):
             sock.close()
             sys.exit(1)
        payload = plaintext.decode('utf-8')
        metada = json.loads(payload)
    except:
        if not metada['ready']:
            print('server ' + config['to'] + ' cannot upload file')
            sock.close()
            sys.exit(1)
    

def send_upload(sock, config):
    # check if file exists
    if not os.path.exists(config['filepath']):
        print('file does not exists: ' + config['filepath']) 
        sock.close()
        sys.exit(1)
    # read the file content
    file_out = open(config['filepath'], "rb")
    file_content = file_out.read()
    cipher=AES.new(config['k'], mode=AES.MODE_GCM)
    ciphertext, MAC = cipher.encrypt_and_digest(file_content)
    sock.sendall(cipher.nonce+MAC+ciphertext)
    file_out.close()    

def receive_download(sock, config):
    # receive data from the server
    data = sock.recv(BUFFER_SIZE)
    file_content = data
    # extract file_content
    nonce=file_content[:DH_NONCE_SIZE]
    MAC=file_content[DH_NONCE_SIZE:2*DH_NONCE_SIZE]
    ciphertext=file_content[2*DH_NONCE_SIZE:]
    cipher=AES.new(config['k'], AES.MODE_GCM, nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, MAC)
        payload = plaintext.decode('utf-8')
        dirname = os.path.dirname(config['filepath'])
        file_out = open(config['filepath'], "wb")
        file_out.write(plaintext)
        file_out.close()
    except: 
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    

# =============================================
# ===== do not modify the code below ==========
# =============================================

def client(config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # handshake
        sock.connect((host, port))
        send_client_hello(sock, config)
        receive_server_hello(sock, config)
        # data exchange
        send_request(sock, config)
        if config['request'] == 'upload':
            receive_ready(sock, config)
            send_upload(sock, config)
        elif config['request'] == 'download':
            receive_download(sock, config)
    
if __name__ == "__main__":
    import os, sys, getopt
    def usage():
        print ('Usage:    ' + os.path.basename(__file__) + ' options filepath ')
        print ('Options:')
        print ('\t -f from, --from=from')
        print ('\t -t to, --to=to')
        print ('\t -r roots, --roots=roots')
        print ('\t -u, --upload')
        print ('\t -d, --download')
        print ('\t -f filename, --filename=filename')
        sys.exit(2)
    try:
      opts, args = getopt.getopt(sys.argv[1:],"hudp:s:f:t:r:f:",["help", "upload", "download", "from=", "to=", "roots=", "filename="])
    except getopt.GetoptError as err:
      print(err)
      usage()
    # extract parameters
    request = None
    fr = None
    to = None
    roots = None
    filename = None
    filepath = args[0] if len(args) > 0 else None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
           usage()
        elif opt in ("-u", "--upload"):
           request = 'upload'
        elif opt in ("-d", "--download"):
           request = 'download'
        elif opt in ("-f", "--from"):
           fr = arg
        elif opt in ("-t", "--to"):
           to = arg
        elif opt in ("-r", "--roots"):
           roots = arg
        elif opt in ("-f", "--filename"):
           filename = arg
    # check arguments
    if (request is None):
       print('upload/download option is missing\n')
       usage()
    if (fr is None):
       print('from option is missing\n')
       usage()
    if (to is None):
       print('to option is missing\n')
       usage()
    if (roots is None):
       print('roots option is missing\n')
       usage()      
    if (filename is None):
       print('filename option is missing\n')
       usage()
    if (filepath is None):
       print('filepath is missing\n')
       usage()
    # create config
    config = {'request': request, 'from': fr, 'filename': filename, 'filepath': filepath}
    # extract server information
    config['to'] = to.split("@")[0]
    host = to.split("@")[1].split(":")[0]
    port = int(to.split(":")[1])
    # extract all root certificates
    if not os.path.exists(roots):
        print('root certificates path does not exists\n')
        usage()
    else:
        list_of_files = os.listdir(roots)
        config['roots']=[]
        for file in list_of_files:
            f = open(os.path.join(roots, file), "r")
            config['roots'].append(f.read())
            f.close()
    # run the client
    client(config)