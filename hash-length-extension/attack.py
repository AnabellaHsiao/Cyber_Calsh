#!/usr/local/bin/python3

import sys
from urllib.parse import urlparse, parse_qs, quote
import http.client
import hlextend

# =============================================
# ========= write your code below  ============
# =============================================

def attack(url):
    # parameter url is the attack url you construct
    parsed = urlparse(url)
    print("----------------")
    print(parsed)
    print("--------------------------")
    # open a connection to the server
    httpconn = http.client.HTTPSConnection(parsed.hostname, parsed.port)
    query =parsed.query.split("&")
    tag=query[0]

    print(tag)



    # issue server-API request
    httpconn.request("GET", parsed.path + "?" + parsed.query)

    # httpresp is response object containing a status value and possible message
    httpresp = httpconn.getresponse()

    # valid request will result in httpresp.status value 200
    print(httpresp.status, file=sys.stderr)

    # in the case of a valid request, print the server's message
    print(httpresp.read(), file=sys.stderr)
    
    # return the url that made the attack successul 
    return parsed.scheme + "://" + parsed.netloc + parsed.path + "?" + parsed.query # dummy code


# =============================================
# ===== do not modify the code below ==========
# =============================================
            
if __name__ == "__main__":
   import os, sys, getopt
   def usage():
        print ('Usage:    ' + os.path.basename(__file__) + ' url ')
        sys.exit(2)
   try:
      opts, args = getopt.getopt(sys.argv[1:],"h",["help"])
   except getopt.GetoptError as err:
      print(err)
      usage()
   # extract parameters
   url = args[0] if len(args) > 0 else None
   # check arguments
   if (url is None):
       print('url is missing\n')
       usage()
   # run the command
   print(attack(url))