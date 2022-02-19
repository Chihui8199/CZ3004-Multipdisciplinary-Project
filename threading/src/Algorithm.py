import logging
import socket
from config import LOCALE, ALGORITHM_SOCKET_BUFFER_SIZE, WIFI_IP, WIFI_PORT


'''
Algorithm will need an accompanying pc_client.py
Algorithm.connect() will wait for Algorithm to connect before proceeding
'''

class Algorithm:
    def __init__(self, host=WIFI_IP, port=WIFI_PORT):
        self.host = host
        self.port = port

        self.client_sock = None
        self.socket = None
        self.address = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        
    def connect(self):
        while True:
            retry = False

            try:
                print('Establishing connection with Algorithm')

                if self.client_sock is None:
                    self.client_sock, self.address = self.socket.accept()
                    print('Successfully connected with Algorithm: ' + str(self.address))
                    retry = False

            except Exception:
                logging.exception("Connection with Algorithm failed")


                if self.client_sock is not None:
                    self.client_sock.close()
                    self.client_sock = None
                retry = True

            if not retry:
                break
            print("Retrying Algorithm connection...")

    def disconnect(self):
        try:
            if self.client_sock is not None:
                self.client_sock.close()
                self.client_sock = None
            
            print("Algorithm disconnected Successfully")

        except Exception:
            logging.exception("Algorithm disconnect failed")

    def disconnect_all(self):
        try:
            if self.client_sock is not None:
                self.client_sock.close()
                self.client_sock = None

            if self.socket is not None:
                self.socket.close()
                self.socket = None

            print("Algorithm disconnected Successfully")

        except Exception:
            logging.exception("Algorithm disconnect_all failed")

    def read(self):
        try:
            message = self.client_sock.recv(ALGORITHM_SOCKET_BUFFER_SIZE).strip()

            if len(message) > 0:
                print('From Algorithm:')
                print(message)
                return message

            return None

        except Exception as error:
            logging.exception("Algorithm read failed")
            raise error

    def write(self, message):
        try:
            print('To Algorithm:')
            print(message)
            self.client_sock.send(message.encode())

        except Exception as error:
            logging.exception("Algorithm write failed")
            raise error
            