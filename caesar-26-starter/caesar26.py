#!/usr/local/bin/python3

# =============================================
# ========= write your code below  ============
# =============================================
import sys




''' encrypts the plaintext with a key
    based on the caesar cipher algorithm
    and returns the ciphertext
    (string, string) -> string
    REQ: key matches [0-9]*
    REQ: plaintext matches [a-z]*
'''


def encrypt(key, plaintext):
    if not plaintext.isalpha():
        print('This is an error message', file=sys.stderr)
    if not key.isnumeric():
        print('This is an error message', file=sys.stderr)

    ciphertext=""
    for index in range(len(plaintext)):
        sum = int(ord(plaintext[index])-97+int(key))%26+97
        if  sum>122:
            sum=sum-25
        ciphertext=ciphertext+chr(sum)
        

    return ciphertext

    
    

    
     

''' decrypts the ciphertext with a key

    based on the caesar cipher algorithm
    and returns the plaintext
    (string, string) -> string
    REQ: key matches [0-9]*
    REQ: ciphertext matches [a-z]*'''    
def decrypt(key, ciphertext):
   

    if not key.isnumeric():
        print('This is an error message', file=sys.stderr)
    plaintext=""
        
      
    for index in range(len(ciphertext)):
        sum=int(ord(ciphertext[index])-97-int(key))%26+97
        if  sum < 97:
            sum=sum+25
        plaintext=plaintext+chr(sum)
    
    
    
    
    return plaintext



  
# =============================================
# ===== do not modify the code below ==========
# =============================================
    
if __name__ == "__main__":
  import os, sys, getopt
  def usage():
       print ('Usage:	' + os.path.basename(__file__) + ' option file ')
       print ('Options:')
       print ('\t -e, --encrypt')
       print ('\t -d, --decrypt')
       print ('\t -k n, --key=n')
    
       sys.exit(2)
  # extract parameters
  try:
     opts, args = getopt.getopt(sys.argv[1:],"hedk:",["help", "encrypt", "decrypt", "key=","secret"])
  except getopt.GetoptError as err:
     print(err)
     usage()
  mode = None
  key = None
  filename = args[0] if len(args) > 0 else None
  for opt, arg in opts:
         if opt in ("-h", "--help"):
             usage()
         elif opt in ("-e", "--encrypt"):
             mode = encrypt
         elif opt in ("-d", "--decrypt"):
             mode = decrypt
         elif opt in ("-k", "--key"):
             key=arg
         elif opt in ("-s", "--secret"):
             mode = decrypt
       
  # check arguments
  if (mode is None):
      print('encrypt/decrypt option is missing\n')
      usage()
  if (key is None):
      print('key option is missing\n')
      usage()
  if (filename is None):
      print('input file is missing\n')
      usage()
  # run the command
  with open(filename, "r") as inputStream:
      data = ' '.join(inputStream.read().split())
      
      print(mode(key,data))