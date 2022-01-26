import cv2
from imutils.video import WebcamVideoStream

num1 = cv2.CascadeClassifier('no1.xml');
num2 = cv2.CascadeClassifier('num2new.xml');
num3 = cv2.CascadeClassifier('no3new.xml');
num4 = cv2.CascadeClassifier('no4new.xml');
num5 = cv2.CascadeClassifier('no5.xml');

#video = cv2.VideoCapture(0);
#video = cv2.VideoCapture('http://192.168.16.16/html/cam_pic_new.php');

video = WebcamVideoStream(src='http://192.168.16.16/html/cam_pic_new.php').start()

while True:
    frame = video.read();
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    one = num1.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)
    two = num2.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=1)
    three = num3.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=1)
    four = num4.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=1)
    five = num5.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=1)
    
    one_found = len(one)
    if one_found != 0:
        for x,y,w,h in one:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num1', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
    
    
    two_found = len(two)
    if two_found != 0:
        for x,y,w,h in two:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num2', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
            
    three_found = len(three)
    if three_found != 0:
        for x,y,w,h in three:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num3', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
    
    four_found = len(four)
    if four_found != 0:
        for x,y,w,h in four:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num4', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
            
    five_found = len(five)
    if five_found != 0:
        for x,y,w,h in five:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num5', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
            
    

    

video.release();
cv2.destroyAllWindows();
