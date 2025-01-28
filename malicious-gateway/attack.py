#!/usr/local/bin/python3

import os, sys, subprocess

def run(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # this is an example on how to run a shell command (iptables for instance) using call (blocking) 
    subprocess.call('iptables -F'.split(' '))
    subprocess.call('iptables -F -t nat'.split(' '))
    subprocess.call('iptables -F -t mangle'.split(' '))

    # this is an example on how to run a shell command (echo for instance) using Popen (non blocking)
    # k=subprocess.Popen('echo -n exec -it mallory bash',shell=True) 
    # k.wait()
    p = subprocess.Popen('echo -n "Welcome to DarkLab" > /shared/index/index.html', shell=True)
    subprocess.call('iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE'.split(' '))
    subprocess.call('iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT'.split(' '))
    subprocess.call('iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT'.split(' '))
    # # and wait for this process to terminate
    p.wait()
    
    # this is an example on how to run a shell command, redirect its output to a pipe and read that pipe while the command is running
    # stderr is redirect to stdout
    # stdout is redirected to the PIPE
    # cwd is the current working directory
    proc = subprocess.Popen('python2.7 -m SimpleHTTPServer 8080', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=r'/shared/index', shell=True)
            # and then terminate the process and exit the python program with the exit code 0
            # this dummy code is going to stop after the reading the first line
    subprocess.call('iptables -t nat -A PREROUTING -p tcp -i eth1 -d 142.1.97.172 --dport 80 -j DNAT --to-destination 10.0.0.3:8080'.split(' '))
    for line in iter(proc.stdout.readline, b''):
            with open(filepath, "w") as text_file:
                liney=line.decode('utf-8')
                if '/?flag'in liney:
                    print(liney.split("/?flag=")[1].split(' ')[0], file=text_file, end='')
                    proc.terminate()
                    sys.exit(0)
    
            
# =============================================
# ===== do not modify the code below ==========
# =============================================
    
if __name__ == "__main__":
    import os, sys, getopt
    def usage():
       print ('Usage:	' + os.path.basename(__file__) + ' filepath ')
       sys.exit(2)
    # extract parameters
    try:
         opts, args = getopt.getopt(sys.argv[1:],"h",["help"])
    except getopt.GetoptError as err:
         print(err)
         usage()
         sys.exit(2)
    filepath = args[0] if len(args) > 0 else None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
           usage()
    if (filepath is None):
        print('filepath is missing\n')
        usage()
    # run the command
    run(filepath)
