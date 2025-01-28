#!/usr/local/bin/python3

import json
from scapy.all import *
from urllib.parse import urlparse, parse_qs

load_layer('http')
load_layer('tls')
load_layer('dns')

results = []

# =============================================
# ========= write your code below  ============
# =============================================

def packet_filter(packet):
    if packet.haslayer(HTTPRequest)or packet.haslayer(HTTPResponse):
        if packet.haslayer(Raw):
            payload = packet[Raw].load
        return True

def packet_process(packet):
    packet.show()
    if packet.haslayer(HTTPRequest):
        request_data = {
            "type": "request",
            "host": packet[HTTPRequest].Host.decode('utf-8'),
            "method": packet[HTTPRequest].Method.decode('utf-8'),
            "path": packet[HTTPRequest].Path.decode('utf-8')
            
        }
        if "?" in str(packet[HTTPRequest].Path) and "=" in str(packet[HTTPRequest].Path):
            request_data["query_args"]={}
            # Extract the query string part after the "?"
            query_string = packet[HTTPRequest].Path.decode('utf-8').split("?")[1]
            # Split the query string by '&' to get individual key-value pairs
            pairs = query_string.split("&")
            # Iterate over the pairs and split them by '=' to get keys and values
            for pair in pairs:
                if "=" in pair:  # Ensure there is an '=' in the pair
                    key, value = pair.split("=")
                    request_data["query_args"][key] = value
                else:  # Handle the case where there is no '=' in the pair
                    request_data["query_args"][pair] = None
        if  packet[HTTPRequest].Cookie!=None:
            request_data["cookies"] = {}
            cookie_header = packet[HTTPRequest].Cookie.decode('utf-8')
            cookie = cookie_header.split(";")
            for cookie_parts in cookie:
                key, value = cookie_parts.split("=", 1)
                request_data["cookies"][key] = value
        if packet.haslayer(Raw):
            request_data["body"]=""
            payload = packet[Raw].load.decode('utf-8')
            request_data["body"]= payload

        if packet.Content_Type!=None and packet.Content_Type.decode() == 'application/x-www-form-urlencoded':
              request_data["form"] = {}
              payload= packet[Raw].load.decode()
              pairs=payload.split("&")
              for pair in pairs:
                if "=" in pair:  # Ensure there is an '=' in the pair
                    key, value = pair.split("=")
                    request_data["form"][key] = value
                else:  # Handle the case where there is no '=' in the pair
                    request_data["form"][pair] = None
        results.append(request_data)
        
    if packet.haslayer(HTTPResponse):
         response_data = {
            "type": "response",
            "status_code": packet[HTTPResponse].Status_Code.decode('utf-8')   
        }
         if packet[HTTPResponse].Set_Cookie!=None:
            response_data["cookies"] = {}
            cookie_header = packet[HTTPResponse].Set_Cookie.decode('utf-8')
            cookie = cookie_header.split(";")
            for cookie_parts in cookie:
                key, value = cookie_parts.split("=", 1)
                if key=="session-id":
                    response_data["cookies"][key] = value
         if packet.haslayer(Raw):
            response_data["body"]=""
            payload = packet[Raw].load.decode('utf-8')
            response_data["body"]= payload
         results.append(response_data)
        
        
         
        
            

        

           



       

            
                  
                  
       



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