#!/usr/local/bin/python3

import json
from scapy.all import *

load_layer('http')
load_layer('tls')
load_layer('dns')

results = []

# =============================================
# ========= write your code below  ============
# =============================================

def packet_filter(packet):
    # filter each TCP request
    return packet.haslayer(TCP)

def packet_process(packet):
    # extract the source and destinations IP
    sip = packet[IPv6].src if (IPv6 in packet) else packet[IP].src
    dip = packet[IPv6].dst if (IPv6 in packet) else packet[IP].dst
    # and the source and destination ports
    sport = str(packet[TCP].sport)
    dport = str(packet[TCP].dport)
    # add a record to the output json file
    results.append({"src": sip, "dst": dip})
    # print a debug message
    print( '{:<6s} {:<16s} -> {:<16s} {}'.format('protocol', sip, dip, 'info'))

# =============================================
# ===== do not modify the code below ==========
# =============================================
    
def run(count, filepath):
    sniff(iface="eth0", lfilter=packet_filter, prn=packet_process, count=count)
    with open(filepath, "w") as file_stream:
        file_stream.write(json.dumps(results, indent=4))
    
if __name__ == "__main__":
    import os, sys, getopt
    def usage():
       print ('Usage:	' + os.path.basename(__file__) + ' filepath ')
       print ('\t -c count, --count=count')
       sys.exit(2)
    # extract parameters
    try:
         opts, args = getopt.getopt(sys.argv[1:],"hc:",["help", "count="])
    except getopt.GetoptError as err:
         print(err)
         usage()
         sys.exit(2)
    count = None
    filepath = args[0] if len(args) > 0 else None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
           usage()
        elif opt in ("-c", "--count"):
           try:
                count = int(arg)
           except ValueError:
                print("count must be a natural number")
                sys.exit(2)
    if (count is None):
        print('count option is missing\n')
        usage()
    if (filepath is None):
        print('filepath is missing\n')
        usage()
    # run the command
    run(count, filepath)