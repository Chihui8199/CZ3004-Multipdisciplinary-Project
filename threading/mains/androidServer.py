from bluetooth import *
from config import RFCOMM_PORT as RFCOMM_PORT, UUID as UUID, ANDROID_BUFFER_SIZE as buffer

__author__ = 'Guo Wanyao'

class androidAPI(object):
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.bt_is_connected = False


    def connect(self):
        """
        Connect to the Nexus 7 device
        """
        # Creating the server socket and bind to port		
        try:
            self.server_socket = BluetoothSocket(RFCOMM)
            self.server_socket.bind(("", RFCOMM_PORT))
            self.server_socket.listen(RFCOMM_PORT)	# Listen for requests
            self.port = self.server_socket.getsockname()[1]

            advertise_service(self.server_socket, "MDP-TEAM16",
                              service_id = UUID,
                              service_classes = [UUID, SERIAL_PORT_CLASS],
                              profiles = [SERIAL_PORT_PROFILE])
            print("Waiting for BT connection on RFCOMM channel %d" % self.port)
            # Accept requests
            self.client_socket, client_address = self.server_socket.accept()
            print("Accepted connection from ", client_address)
            self.bt_is_connected = True

        except Exception as e:
            print("Error: %s" %str(e))


    def close_bt_socket(self):
        """
        Close socket connections
        """
        if self.client_socket:
            self.client_socket.close()
            print("Closing client socket")
        if self.server_socket:
            self.server_socket.close()
            print("Closing server socket")
        self.bt_is_connected = False


    def bt_is_connect(self):
        """
        Check status of BT connection
        """
        return self.bt_is_connected


    def write(self, message):
        """
        Write message to Nexus
        """
        try:
            self.client_socket.send(str(message))
        except BluetoothError:
            print("Bluetooth Error. Connection reset by peer")
            self.connect()	# Reestablish connection

            
    def read(self):
        """
        Read incoming message from Nexus
        """
        try:
            msg = self.client_socket.recv(buffer)
            return msg
        except BluetoothError:
            print("Bluetooth Error. Connection reset by peer. Trying to connect...")
            self.connect()	# Reestablish connection


# if __name__ == "__main__":
#     print "Running Main"
#     bt = AndroidAPI()
#     bt.connect()
    
#     # send_msg = raw_input()
#     # print "Write(): %s " % send_msg
#     # bt.write(send_msg)

#     print "read"
#     print "data received: %s " % bt.read()

#     print "closing sockets"
#     bt.close_bt_socket()

