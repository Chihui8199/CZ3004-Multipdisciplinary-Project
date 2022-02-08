#!/usr/bin/env python2
import socket
from config import WIFI_IP as serverIP, WIFI_PORT as serverPort

__author__ = "Guo Wanyao"


HOST = serverIP  # The server's hostname or IP address
PORT = serverPort        # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:    
    s.connect((HOST, PORT))
## testing send streaming
    while True:
        data = raw_input()
        if data:
            s.sendall(data)
        data= s.recv(1024)
        if data:
            print('Received %s' %repr(data))

## testing recieve streaming
    # while True:
    #    data= s.recv(1024)
    #    if data:
    #        print'Received %s' %repr(data)
except:
    print("server not started")
