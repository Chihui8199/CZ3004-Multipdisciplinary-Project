import time
from datetime import datetime
from multiprocessing import Process, Value, Queue, Manager

from Android import Android
from Robot import Robot
from Algorithm import Algorithm
from protocols import *      

class MultiProcessComms:
    """
    This class handles multi-processing communications between Robot, Algorithm and Android.
    """
    def __init__(self):
        """
        Instantiates a MultiProcess Communications session and set up the necessary variables.

        Upon instantiation, RPi begins connecting to
        - Robot
        - Algorithm
        - Android
        in this exact order.

        Also instantiates the queues required for multiprocessing.
        """
        print('Initializing Multiprocessing Communication')

        self.robot = Robot()  # handles connection to Robot
        self.algorithm = Algorithm()  # handles connection to Algorithm
        self.android = Android()  # handles connection to Android
        
        self.manager = Manager()

        # messages from Robot, Algorithm and Android are placed in this queue before being read
        self.message_queue = self.manager.Queue()
        self.to_android_message_queue = self.manager.Queue()

        self.read_robot_process = Process(target=self._read_robot)
        self.read_algorithm_process = Process(target=self._read_algorithm)
        self.read_android_process = Process(target=self._read_android)
        
        self.write_process = Process(target=self._write_target)
        self.write_android_process = Process(target=self._write_android)

        self.dropped_connection = Value('i',0) # 0 - Robot, 1 - algorithm

    def start(self):        
        try:
            self.robot.connect()
            # self.algorithm.connect()
            self.android.connect()

            # print('Connected to Robot, Algorithm and Android')
            print('Connected to Robot and Android')

            self.read_robot_process.start()
            # self.read_algorithm_process.start()
            self.read_android_process.start()
            self.write_process.start()
            self.write_android_process.start()
            
            # print('Started all processes: read-Robot, read-algorithm, read-android, write, image')
            print('Started processes: read-Robot, read-android, write')


            print('Multiprocess communication session started')
            
        except Exception as error:
            raise error

        self._allow_reconnection()

    def end(self):
        # children processes should be killed once this parent process is killed
        # self.algorithm.disconnect_all()
        self.android.disconnect_all()
        print('Multiprocess communication session ended')

    def _allow_reconnection(self):
        print('You can reconnect to RPi after disconnecting now')

        while True:
            try:
                if not self.read_robot_process.is_alive():
                    self._reconnect_robot()
                    
                # if not self.read_algorithm_process.is_alive():
                #     self._reconnect_algorithm()
                    
                if not self.read_android_process.is_alive():
                    self._reconnect_android()
                    
                if not self.write_process.is_alive():
                    if self.dropped_connection.value == 0:
                        self._reconnect_robot()
                    elif self.dropped_connection.value == 1:
                        self._reconnect_algorithm()
                        
                if not self.write_android_process.is_alive():
                    self._reconnect_android()
                                    
            except Exception as error:
                print("Error during reconnection: ",error)
                raise error

    def _reconnect_robot(self):
        self.robot.disconnect()
        
        self.read_robot_process.terminate()
        self.write_process.terminate()
        self.write_android_process.terminate()

        self.robot.connect()

        self.read_robot_process = Process(target=self._read_robot)
        self.read_robot_process.start()

        self.write_process = Process(target=self._write_target)
        self.write_process.start()
        
        self.write_android_process = Process(target=self._write_android)
        self.write_android_process.start()

        print('Reconnected to Robot')

    # def _reconnect_algorithm(self):
    #     self.algorithm.disconnect()
        
    #     self.read_algorithm_process.terminate()
    #     self.write_process.terminate()
    #     self.write_android_process.terminate()

    #     self.algorithm.connect()

    #     self.read_algorithm_process = Process(target=self._read_algorithm)
    #     self.read_algorithm_process.start()

    #     self.write_process = Process(target=self._write_target)
    #     self.write_process.start()
        
    #     self.write_android_process = Process(target=self._write_android)
    #     self.write_android_process.start()

    #     print('Reconnected to Algorithm')

    def _reconnect_android(self):
        self.android.disconnect()
        
        self.read_android_process.terminate()
        self.write_process.terminate()
        self.write_android_process.terminate()
        
        self.android.connect()
        
        self.read_android_process = Process(target=self._read_android)
        self.read_android_process.start()

        self.write_process = Process(target=self._write_target)
        self.write_process.start()
        
        self.write_android_process = Process(target=self._write_android)
        self.write_android_process.start()

        print('Reconnected to Android')
        
    def _read_robot(self):
        while True:
            try:
                raw_message = self.robot.read()
                
                if raw_message is None:
                    continue

                message_list = raw_message.splitlines()
                
                for message in message_list:
                
                    if len(message) <= 0:
                        continue    
                        
                    self.message_queue.put_nowait(self._format_for(
                        ALGORITHM_HEADER, 
                        message[1:] + NEWLINE
                    ))
                    
            except Exception as error:
                print('Process read_Robot failed: ' + str(error))
                break    

    # def _read_algorithm(self):
    #     while True:
    #         try:
    #             raw_message = self.algorithm.read()
                
    #             if raw_message is None:
    #                 continue
                
    #             message_list = raw_message.splitlines()
                
    #             for message in message_list:
                
    #                 if len(message) <= 0:
    #                     continue

    #                 elif message[0] == AlgorithmToAndroid.SEND_STATUS:
    #                     self.to_android_message_queue.put_nowait( 
    #                         message[1:] + NEWLINE
    #                     )
                    
    #                 else:  # message[0] == 'I'
    #                     self.message_queue.put_nowait(self._format_for(
    #                         ROBOT_HEADER, 
    #                         message[1:] + NEWLINE
    #                     ))
                
    #         except Exception as error:
    #             print('Process read_algorithm failed: ' + str(error))
    #             break

    def _read_android(self):
        while True:
            try:
                raw_message = self.android.read()
                
                if raw_message is None:
                    continue
                
                message_list = raw_message.splitlines()
                
                for message in message_list:
                    if len(message) <= 0:
                        continue

                    elif message[0] in (AndroidToRobot.ALL_MESSAGES):
                        if message[0] == AndroidToRobot.MOVE_UP:
                            self.message_queue.put_nowait(self._format_for(
                            ROBOT_HEADER, "f0501000149" + NEWLINE
                        ))
                        elif message[0] == AndroidToRobot.MOVE_BACK:
                            self.message_queue.put_nowait(self._format_for(
                            ROBOT_HEADER, "b0501000149" + NEWLINE
                        ))
                        elif message[0] == AndroidToRobot.TURN_LEFT:
                            self.message_queue.put_nowait(self._format_for(
                            ROBOT_HEADER, "f0501000127" + NEWLINE
                        ))
                        else:
                            self.message_queue.put_nowait(self._format_for(
                            ROBOT_HEADER, "f0501000200" + NEWLINE
                        ))
                        
                    else:
                        self.message_queue.put_nowait(self._format_for(
                            ALGORITHM_HEADER, 
                            message[1:] + NEWLINE
                        ))
                    
            except Exception as error:
                print('Process read_android failed: ' + str(error))
                break
    
    # def _read_android(self):
    #     while True:
    #         try:
    #             raw_message = self.android.read()
                
    #             if raw_message is None:
    #                 continue
                
    #             message_list = raw_message.splitlines()
                
    #             for message in message_list:
    #                 if len(message) <= 0:
    #                     continue

    #                 elif message in (AndroidToRobot.ALL_MESSAGES):
    #                     self.message_queue.put_nowait(self._format_for(
    #                         ROBOT_HEADER, message[1:] + NEWLINE
    #                     ))
                        
    #                 else:
    #                     self.message_queue.put_nowait(self._format_for(
    #                         ALGORITHM_HEADER, 
    #                         message[1:] + NEWLINE
    #                     ))
                    
    #         except Exception as error:
    #             print('Process read_android failed: ' + str(error))
    #             break

    def _write_target(self):
        while True:
            target = None
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    target, payload = message['target'], message['payload']

                    if target == ROBOT_HEADER:
                        self.robot.write(payload)
                        
                    # elif target == ALGORITHM_HEADER:
                    #     self.algorithm.write(payload)
                        
                    else:
                        print("Invalid header", target)
                
            except Exception as error:
                print('Process write_target failed: ' + str(error))

                if target == ROBOT_HEADER:
                    self.dropped_connection.value = 0

                elif target == ALGORITHM_HEADER:
                    self.dropped_connection.value = 1

                break
                
    def _write_android(self):
        while True:
            try:
                if not self.to_android_message_queue.empty():
                    message = self.to_android_message_queue.get_nowait()
                    
                    self.android.write(message)
                
            except Exception as error:
                print('Process write_android failed: ' + str(error))
                break

    def _format_for(self, target, payload):
        return {
            'target': target,
            'payload': payload,
        }