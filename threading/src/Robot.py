import serial
import logging
from config import SERIAL_PORT, BAUD_RATE, LOCALE


"""
Robot will need an accompanying script to receive the data from Rpi
Communication has to be two ways, Rpi send, Robot receive and reply, Rpi receive
Note: RPi write > Robot read and write > RPi can write again
"""

class Robot:
    def __init__(self, serial_port=SERIAL_PORT, baud_rate=BAUD_RATE):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.connection = None

    def connect(self):
        count = 1000000
        while True:
            retry = False

            try:
                if count >= 1000000:
                    print('Establishing connection with Robot')

                self.connection = serial.Serial(self.serial_port, self.baud_rate)

                if self.connection is not None:
                    print('Successfully connected with Robot: ' + str(self.connection.name))
                    retry = False

            except Exception as error:
                if count >= 1000000:
                    print('Connection with Robot failed: ' + str(error))

                retry = True

            if not retry:
                break

            if count >= 1000000:
                print('Retrying Robot connection...')
                count=0

            count += 1

    def disconnect(self):
        try:
            if self.connection is not None:
                self.connection.close()
                self.connection = None

                print('Successfully closed connection with Robot')

        except Exception:
            logging.exception("Robot disconnect failed")
            
    def read(self):
        try:
            message = self.connection.readline().strip()
            print('From Robot:')
            print(message)

            if len(message) > 0:
                return message

            return None

        except Exception as error:
            logging.exception("Robot read failed")
            raise error
    
    def write(self, message):
        try:
            print('To Robot:')
            print(message)
            self.connection.write(message)

        except Exception as error:
            logging.exception("Robot read failed")
            raise error
