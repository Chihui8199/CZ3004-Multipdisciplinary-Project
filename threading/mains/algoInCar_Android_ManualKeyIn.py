#!/usr/bin/env python2
from robotServer import robotAPI
from androidServer import androidAPI
from pcServer import pcAPI
from config import *
from picamera import PiCamera
from picamera.array import PiRGBArray

import Queue
import thread
import threading
import os
import time

# For testing
import datetime

__author__ = "Guo Wanyao"


class Main:
    def __init__(self):
        # allow rpi android to be discoverable
        os.system("sudo hciconfig hci0 piscan")
        # initial connections
        self.android = androidAPI()
        self.robot = robotAPI()
        self.pc = pcAPI()
        # first establish
        self.android.connect()
        # second establish
        self.pc.init_pc_comm()
        # third establish
        self.robot.connect_serial()

        print("All end-devices are connected\n")

        # initialize queues
        self.Aqueue = Queue.Queue(maxsize=0)
        self.Rqueue = Queue.Queue(maxsize=0)
        self.Pqueue = Queue.Queue(maxsize=0)
        # initialization done

    # read/write Android
    def readAndroid(self, Pqueue):
        while 1:
            msg = raw_input("read from Android:\n")
            Pqueue.put_nowait(msg)
            f.write("Read from BT: %s\n" % msg)


    def writeAndroid(self, Aqueue):
        while 1:
            if not Aqueue.empty():
                msg = Aqueue.get_nowait()
                print("Write to android: %s\n" % msg)
                f.write("Write to android: %s\n" % msg)

    # read/write Robot
    def readRobot(self, Pqueue):
        while 1:
            if self.robot.is_robot_connected:
                msg = self.robot.read_from_serial()
                if msg:
                    Pqueue.put_nowait(msg)
                    print("Read from Robot: %s\n" % msg)
                    f.write("Read from Robot: %s\n" % msg)

    # read/write Robot
    def readRobot2(self, Pqueue):
        while 1:
            msg = raw_input("read from robot:\n")
            if msg:
                Pqueue.put_nowait(msg)

    def writeRobot(self, Rqueue):
        while 1:
            if not Rqueue.empty():
                msg = Rqueue.get_nowait()
                self.robot.write_to_serial(msg)
                print("Write to Robot: %s\n" % msg)
                f.write("Write to Robot: %s\n" % msg)

    # read/write PC
    def readPC(self, Rqueue, Aqueue, Pqueue):
        while 1:
            if self.pc.pc_is_connected:
                msg = self.pc.read_from_PC()
                if msg:
                    destination = msg[0]
                    dataBody = msg[1:]
                    print("Read from PC: %s\n" % msg)
                    f.write("Read from PC: %s\n" % msg)
                    if destination == 'a':
                        Aqueue.put_nowait(dataBody)
                    elif destination == 'r':
                        Rqueue.put_nowait(dataBody)
                    # No image recognition for now
                    # trigger camera
                    # elif destination == 'c':
                    #     image_array = self.take_pic()
                        # print "image array: %s" %image_array
                    else:
                        print("unknown destination for pc message")
                        f.write("unknown destination for pc message")

    def writePC(self, Pqueue):
        while 1:
            if not Pqueue.empty():
                msg = Pqueue.get_nowait()
                if msg:
                    self.pc.write_to_PC(msg + "\n")
                    print("Write to PC: %s\n" % msg)
                    f.write("Write to PC: %s\n" % msg)

    # def take_pic(self):
    #     start_time = datetime.now()
    #     try:
    #         # initialize the camera and grab a reference to the raw camera capture
    #         camera = PiCamera(resolution=(IMAGE_WIDTH, IMAGE_HEIGHT))  # '1920x1080'
    #         rawCapture = PiRGBArray(camera)
            
    #         # allow the camera to warmup
    #         time.sleep(0.1)
            
    #         # grab an image from the camera
    #         camera.capture(rawCapture, format=IMAGE_FORMAT)
    #         image = rawCapture.array
    #         camera.close()

    #         print('Time taken to take picture: ' + str(datetime.now() - start_time) + 'seconds')
            
    #         # to gather training images
    #         # os.system("raspistill -o images/test"+
    #         # str(start_time.strftime("%d%m%H%M%S"))+".png -w 1920 -h 1080 -q 100")
        
    #     except Exception as error:
    #         print('Taking picture failed: ' + str(error))
        
    #     return image

    def Mthreads(self):
        try:
            # 1: Read from android
            thread.start_new_thread(self.readAndroid, (self.Pqueue,))
            # 2: Write to PC
            thread.start_new_thread(self.writePC, (self.Pqueue,))
            # 3: Read from PC
            thread.start_new_thread(self.readPC, (self.Rqueue, self.Aqueue, self.Pqueue,))
            # 4: Write to Robot
            thread.start_new_thread(self.writeRobot, (self.Rqueue,))
            # 5: Write to Android
            thread.start_new_thread(self.writeAndroid, (self.Aqueue,))
            # 6: Read from Robot
            thread.start_new_thread(self.readRobot, (self.Pqueue,))

        except Exception as e:
            print("Error in Mthreadings of Exploration %s" % str(e))
            f.write("Error in Mthreadings of Exploration %s" % str(e))
        while 1:
            pass


# Driver code
try:
    f = open('log.txt', 'w+')
    main = Main()
    main.Mthreads()

except KeyboardInterrupt:
    print("Terminating the main program now...")
    f.write("Terminating the main program now...")