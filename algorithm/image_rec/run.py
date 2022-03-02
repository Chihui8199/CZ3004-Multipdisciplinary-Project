import threading
from multiprocessing.dummy import Process
from detect import *
from img_rec import *
import time

detect_sem = threading.Lock()
exit_flag = False

def async_detect(stop):
    count=0
    while(True):
        time.sleep(5)    
        detect_sem.acquire()
        id, id_num, dist, angle = detect()
        detect_sem.release()
        if exit_flag:
            break



async_detect_thread = Process(target= async_detect,args=(lambda: exit_flag,))
async_detect_thread.start()
count=0
while(count!=10):
    time.sleep(1)
    print("ALGO RUNNING")
    count = count + 1
print("ALGO DONE")
exit_flag = True
async_detect_thread.join()


#async_detect_thread.join()

