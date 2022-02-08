from dataclasses import is_dataclass
import string
import cv2
from imutils.video import WebcamVideoStream

def detect(obj, msg, image, frame,found):
    if found != 0:
        for x,y,w,h in obj:
            frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, msg, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            cv2.imshow('Image Recognition', frame)
            #cv2.imwrite(image,frame)
            key = cv2.waitKey(1) & 0xFF

num1 = cv2.CascadeClassifier('num1.xml')
num2 = cv2.CascadeClassifier('finalno2.xml')
num3 = cv2.CascadeClassifier('num3.xml')
num4 = cv2.CascadeClassifier('num4.xml')
num5 = cv2.CascadeClassifier('5.xml')
num6 = cv2.CascadeClassifier('num6.xml')
num7 = cv2.CascadeClassifier('num7.xml')
num8 = cv2.CascadeClassifier('num8.xml')
num9 = cv2.CascadeClassifier('num9.xml')
alphabetA = cv2.CascadeClassifier('A.xml')
alphabetB = cv2.CascadeClassifier('B_new.xml')
alphabetC = cv2.CascadeClassifier('C.xml')
alphabetD = cv2.CascadeClassifier('D.xml')
alphabetE = cv2.CascadeClassifier('E.xml')
alphabetF = cv2.CascadeClassifier('F.xml')
alphabetG = cv2.CascadeClassifier('G_new.xml')
alphabetH = cv2.CascadeClassifier('H.xml')
alphabetS = cv2.CascadeClassifier('S.xml')
alphabetT = cv2.CascadeClassifier('T.xml')
alphabetU = cv2.CascadeClassifier('U.xml')
alphabetV = cv2.CascadeClassifier('V.xml')
alphabetW = cv2.CascadeClassifier('W.xml')
alphabetX = cv2.CascadeClassifier('X.xml')
alphabetY = cv2.CascadeClassifier('Y.xml')
alphabetZ = cv2.CascadeClassifier('Z.xml')
circlexml = cv2.CascadeClassifier('circle.xml')
upArrowxml = cv2.CascadeClassifier('uparrow.xml')
downArrowxml = cv2.CascadeClassifier('downarrow.xml')
rightArrowxml = cv2.CascadeClassifier('rightarrow.xml')
leftArrowxml = cv2.CascadeClassifier('leftarrow.xml')
'''





bullseyexml = cv2.CascadeClassifier(bullseye.xml)
''' 

#video = cv2.VideoCapture(0);
#video = cv2.VideoCapture('http://192.168.16.16/html/cam_pic_new.php');

#video = WebcamVideoStream(src='http://192.168.16.16/html/cam_pic_new.php').start()
video = WebcamVideoStream(src=0).start()
count = 0
while True:
    frame = video.read()
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    one = num1.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=10)#ok
    two = num2.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    three = num3.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)#ok
    four = num4.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    five = num5.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    six = num6.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    seven = num7.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)#ok
    eight = num8.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    nine = num9.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    A =  alphabetA.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#retrain
    B =  alphabetB.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=12)#ok
    C =  alphabetC.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    D =  alphabetD.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    E =  alphabetE.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=9)#ok
    F =  alphabetF.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=7)#ok
    G =  alphabetG.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)#ok
    H = alphabetH.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    S = alphabetS.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=3)#ok
    T = alphabetT.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    U = alphabetU.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=9)#ok
    V = alphabetV.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=12)#ok
    W = alphabetW.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=6)#ok
    X = alphabetX.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    Y = alphabetY.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    Z = alphabetZ.detectMultiScale(frame,scaleFactor=1.02, minNeighbors=2)#kinda
    circle = circlexml.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#retrain
    upArrow = upArrowxml.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=5)#ok
    downArrow = downArrowxml.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=12)#ok
    rightArrow = rightArrowxml.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)#ok
    leftArrow = leftArrowxml.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=4)#ok
    '''
    
    
    bullseye = bullseye.detectMultiScale(frame,scaleFactor=1.05, minNeighbors=2)
    '''
    
    one_found = len(one)
    two_found = len(two)
    three_found = len(three)
    four_found = len(four)
    five_found = len(five)
    six_found = len(six)
    seven_found = len(seven)
    eight_found = len(eight)
    nine_found = len(nine)
    A_found = len(A)
    B_found = len(B)
    C_found = len(C)
    D_found = len(D)
    E_found = len(E)
    F_found = len(F)
    G_found = len(G)
    H_found = len(H)
    S_found = len(S)
    T_found = len(T)
    U_found = len(U)
    V_found = len(V)
    W_found = len(W)
    X_found = len(X)
    Y_found = len(Y)
    Z_found = len(Z)
    circle_found = len(circle)
    uparrow_found = len(upArrow)
    downarrow_found = len(downArrow)
    rightarrow_found = len(rightArrow)
    leftarrow_found = len(leftArrow)

    detect(one,"Num1 ID=11", 'images/1.png',frame,one_found)
    detect(two,'Num2 ID=12', 'images/2.png',frame,two_found)
    detect(three,'Num3 ID=13', 'images/3.png',frame,three_found)
    detect(four,'Num4 ID=14', 'images/4.png',frame,four_found)
    detect(five,'Num5 ID=15', 'images/5.png',frame,five_found)
    detect(six,'Num6 ID=16', 'images/6.png',frame, six_found)
    detect(seven,'Num7 ID=17', 'images/7.png',frame, seven_found)
    detect(eight,'Num8 ID=18', 'images/8.png',frame, eight_found)
    detect(nine,'Num9 ID=19', 'images/9.png',frame, nine_found)
    detect(A,'A ID=20', 'images/A.png',frame, A_found)
    detect(B,'B ID=21', 'images/B.png',frame, B_found)
    detect(C,'C ID=22', 'images/C.png',frame,C_found)
    detect(D,'D ID=23', 'images/D.png',frame,D_found)
    detect(E,'E ID=24', 'images/E.png',frame,E_found)
    detect(F,'F ID=25', 'images/F.png',frame,F_found)
    detect(G,'G ID=26', 'images/G.png',frame,G_found)
    detect(H,'H ID=27', 'images/H.png',frame,H_found)
    detect(S,'S ID=28', 'images/S.png',frame,S_found)
    detect(T,'T ID=29', 'images/T.png',frame,T_found)
    detect(U,'U ID=30', 'images/U.png',frame,U_found)
    detect(V,'V ID=31', 'images/V.png',frame,V_found)
    detect(W,'W ID=32', 'images/W.png',frame,W_found)
    detect(X,'X ID=33', 'images/X.png',frame,X_found)
    detect(Y,'Y ID=34', 'images/Y.png',frame,Y_found)
    detect(Z,'Z ID=35', 'images/Z.png',frame,Z_found)
    detect(circle, 'circle ID=40', 'images/circle.png', frame, circle_found)
    detect(upArrow, 'upArrow ID=36', 'images/up.png', frame, uparrow_found)   
    detect(downArrow, 'downArrow ID=37', 'images/down.png', frame, downarrow_found) 
    detect(rightArrow, 'rightArrow ID=38', 'images/right.png', frame, rightarrow_found) 
    detect(leftArrow, 'leftArrow ID=38', 'images/left.png', frame, leftarrow_found) 
    

    

video.release()
cv2.destroyAllWindows()



