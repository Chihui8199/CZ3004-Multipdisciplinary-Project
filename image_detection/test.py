import cv2;

num1 = cv2.CascadeClassifier('no1.xml');
num2 = cv2.CascadeClassifier('num2new.xml');

video = cv2.VideoCapture(0);

while True:
    check, frame = video.read();
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    one = num1.detectMultiScale(frame,scaleFactor=1.1, minNeighbors=3);
    two = num2.detectMultiScale(frame,scaleFactor=1.1, minNeighbors=3);
    
    one_found = len(one)
    if one_found != 0:
        for x,y,w,h in one:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num1', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
    
    
    two_found = len(two)
    if two_found != 0:
        for x,y,w,h in two:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3);
            cv2.putText(frame, 'Num2', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
    
    cv2.imshow('Image Recognition', frame);

    key = cv2.waitKey(1);

    if key == ord('q'):
        break;

video.release();
cv2.destroyAllWindows();
