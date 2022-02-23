import os
import cv2
import numpy as np

directory = 'C:/Users/mdzak/Desktop/yolov5/runs/detect/exp'
count = 0
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if(count==0):
        image1 = cv2.imread(str(f))
        image1 = cv2.resize(image1,(200,200))
        combine = image1
    if(count==1):
       image2 = cv2.imread(str(f))
       image2 = cv2.resize(image2,(200,200))
       combine = np.hstack([image1,image2])
    if(count==2):
        image3 = cv2.imread(str(f))
        image3 = cv2.resize(image3,(200,200))
        combine =  np.hstack([image1,image2,image3])
    if(count==3):
        image4 = cv2.imread(str(f))
        image4 = cv2.resize(image4,(200,200))
        h1 = np.hstack([image1, image2])
        h2 = np.hstack([image3, image4])
        combine = np.vstack([h1,h2])
    if(count==4):
        image5 = cv2.imread(str(f))
        image5 = cv2.resize(image5,(400,200))
        combine = np.vstack([h1,h2,image5])
    if(count==5):
        image6 = cv2.imread(str(f))
        image6 = cv2.resize(image6,(200,200))
        image5 = cv2.resize(image5,(200,200))
        h1 = np.hstack([image1, image2, image3])
        h2 = np.hstack([image4, image5, image6])
        combine = np.vstack([h1,h2])
    if(count==6):
        image7 = cv2.imread(str(f))
        image7 = cv2.resize(image7,(600,200))
        combine = np.vstack([h1,h2,image7])
    if(count==7):
        image8 = cv2.imread(str(f))
        image8 = cv2.resize(image8,(300,200))
        image7 = cv2.resize(image7,(300,200))
        h3 = np.hstack([image7,image8])
        combine = np.vstack([h1,h2,h3])


    count = count +1

cv2.imwrite('C:/Users/mdzak/Desktop/yolov5/result/final.png', combine)
cv2.imshow("Final Collage",combine)
cv2.waitKey(0)
cv2.destroyAllWindows()

    
