import cv2
from imutils.video import WebcamVideoStream

num1 = cv2.CascadeClassifier('no1.xml')
num2 = cv2.CascadeClassifier('finalno2.xml')
num3 = cv2.CascadeClassifier('num3.xml')
num4 = cv2.CascadeClassifier('no4new.xml')
num5 = cv2.CascadeClassifier('no5.xml')
num6 = cv2.CascadeClassifier('num6.xml')
num7 = cv2.CascadeClassifier('num7.xml')
num8 = cv2.CascadeClassifier('num8.xml')
num9 = cv2.CascadeClassifier('num9.xml')

#video = cv2.VideoCapture(0);
#video = cv2.VideoCapture('http://192.168.16.16/html/cam_pic_new.php');

#video = WebcamVideoStream(src='http://192.168.16.16/html/cam_pic_new.php').start()
video = WebcamVideoStream(src=0).start()

while True:
    frame = video.read();
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    one = num1.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)
    two = num2.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)
    three = num3.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)
    four = num4.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)
    five = num5.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=6)
    six = num6.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)
    seven = num7.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)
    eight = num8.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)
    nine = num9.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)
    
    one_found = len(one)
    if one_found != 0:
        for x,y,w,h in one:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num1', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
            cv2.imshow('Image Recognition', frame)
            key = cv2.waitKey(1) & 0xFF
    
    
    
    

    

video.release();
cv2.destroyAllWindows();

