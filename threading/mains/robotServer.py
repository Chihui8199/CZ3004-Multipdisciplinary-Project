import serial
import time
from config import BAUD as baud, SER_PORT0 as ser_port


__author__ = "Guo Wanyao"

class robotAPI(object):
	def __init__(self):
		self.port = ser_port
		self.baud_rate = baud
		self.ser = None
		self.is_robot_connected = False

	def connect_serial(self):
		"""
		Initialize serial socket
		"""
		try:
			self.ser = serial.Serial(self.port, self.baud_rate)
			print("Serial link connected")
			self.is_robot_connected = True
		except Exception as e:
			print("Error: Serial connection not established.")


	def close_sr_socket(self):
		if (self.ser):
			self.ser.close()
			print("Closing serial socket")
			self.is_robot_connected = False


	def write_to_serial(self, msg):
		"""
		Write to robot
		"""
		try:
			self.ser.write(msg)
			# print "Write to robot: %s " % msg
		except Exception:
			print("Error in serial comm. No value to be written. Check connection!")

	def read_from_serial(self):
		"""
		Read from robot

		Waits until data is received from robot
		"""
		try:
			received_data = self.ser.readline()
			# print "Received from robot: %s " % received_data
			return received_data
		except Exception:
			print("Error in serial comm. No value received. Check connection!")



# print "Running Main"
# sr = robotAPI()
# sr.connect_serial()

# send_msg = raw_input()
# print "Writing [%s] to robot" % send_msg
# sr.write_to_serial(send_msg)

# print "read"
# print "data received from serial" % sr.read_from_serial

# print "closing sockets"
# sr.close_sr_socket()