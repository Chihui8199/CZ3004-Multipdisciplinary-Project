import cv2
from imutils.video import WebcamVideoStream
import os
num1 = cv2.CascadeClassifier('no1.xml')
num2 = cv2.CascadeClassifier('finalno2.xml')
num3 = cv2.CascadeClassifier('num3.xml')
num4 = cv2.CascadeClassifier('no4new.xml')
num5 = cv2.CascadeClassifier('no5.xml')

#video = cv2.VideoCapture(0);
#video = cv2.VideoCapture('http://192.168.16.16/html/cam_pic_new.php');

#video = WebcamVideoStream(src='http://192.168.16.16/html/cam_pic_new.php').start()
video = WebcamVideoStream(src=0).start()

while True:
    frame = video.read();
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    one = num1.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)
    two = num2.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)
    three = num3.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)
    four = num4.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)
    five = num5.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)
    
    one_found = len(one)
    if one_found != 0:
        test = os.system("echo “num1” > /dev/rfcomm0")
        for x,y,w,h in one:
            test2 = os.system("echo %d > /dev/rfcomm0" %(x))
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num1', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
    
    
    two_found = len(two)
    if two_found != 0:
        test = os.system("echo “num2” > /dev/rfcomm0")
        for x,y,w,h in two:
            test2 = os.system("echo %d > /dev/rfcomm0" %(x))
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num2', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
            
    three_found = len(three)
    if three_found != 0:
        test = os.system("echo “num3” > /dev/rfcomm0")
        for x,y,w,h in three:
            test2 = os.system("echo %d > /dev/rfcomm0" %(x))
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num3', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
    
    four_found = len(four)
    if four_found != 0:
        test = os.system("echo “num4” > /dev/rfcomm0")
        for x,y,w,h in four:
            test2 = os.system("echo %d > /dev/rfcomm0" %(x))
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num4', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
            
    five_found = len(five)
    if five_found != 0:
        test = os.system("echo “num5” > /dev/rfcomm0")
        for x,y,w,h in five:
            test2 = os.system("echo %d > /dev/rfcomm0" %(x))
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num5', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
            
    

    

video.release();
cv2.destroyAllWindows();


