from img_rec import *

async_detect_thread = Process(target= sync.async_detect,args=(lambda: sync.exit_flag,))
async_detect_thread.start()

#RUN ALGO
count=0
while(count!=20):
    time.sleep(1)
    print("ALGO RUNNING")
    sync.detect_sem.acquire()
    id, id_num, dist, angle = detect()
    print("ALGO CALL DETECT")
    sync.detect_sem.release()
    count = count + 1

#END OF ALGO CODE

sync.stop_async(async_detect_thread)
print("TERMINATED")