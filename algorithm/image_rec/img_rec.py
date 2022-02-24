
#from detect import *
from image_rec.detect import *
from image_rec.detect import *
from cv2 import *
import uuid
import os
import numpy as np
def run_model(filename):#IGNORE
    id, box_size, angle = run(source=ROOT / filename)
    return id, box_size, angle

def run_bullseye(filename):#IGNORE
    id, box_size, angle = runbullseye(source=ROOT / filename)
    return id, box_size, angle

def detect():
    imageId = {"1":11,"2":12,"3":13, "4":14,"5":15,"6":16,"7":17,"8":18,"9":19, 
                    "A":20, "B":21,"C":22,"D":23,"E":24 ,"F":25,"G":26, "H":27, 
                    "S":28,"T":29,"U":30,"V":31, "W":32, "X":33 ,"Y":34,"Z":35, 
                    "up_arrow":36, "down_arrow":37,"right_arrow":38,"left_arrow":39,"circle":40}
    ROOT = FILE.parents[0]
    filename = str(uuid.uuid4())
    #filename = "data/images/" + filename + ".png
    save_dir = increment_path(Path('C:/Users/mdzak/Documents/GitHub/cx3004/algorithm/image_rec/data/images') / "img", exist_ok=False)
    save_dir.mkdir(parents=True, exist_ok=True)
    #print(str(save_dir))
    img_file = str(save_dir)+'/'+filename+'.png'
    filepath = str(save_dir)
    #cam_port = 'http://192.168.16.16/html/cam_pic_new.php' #PI CAMERA
    cam_port = 0 #LAPTOP CAMERA
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    if result:
        cv2.imwrite(img_file, image) #save captured image to file path
    id, box_size, angle= run_model(filepath) #run detection model on image in filepath

    if(box_size!=0):
        box_size = int(int(box_size)/1000) 
        box_size = 0.077*(box_size)*(box_size)-3.98*(box_size)+53.49

    '''if(angle != 0):
        print("raw angle is:", angle)
        if(angle == 300):
            angle = 0
        elif(angle > 300):
            angle = (angle - 300)/9.65
            print("more than 300")
        elif(angle < 300):
            angle = -1*(31.1 - 0.104*(angle))
            print("less than 300")'''
    if(id != "None"):
        id_num = imageId[id]
    else:
        id_num = 0
    print("IMAGE DETECTED IS: ",id)
    print("IMAGE ID IS: ", id_num)
    print("DIST FROM ROBOT IS: ", int(box_size))
    print("ANGLE IS: ", int(angle))
    return id,id_num, int(box_size), int(angle)

def stitch():
    directory = 'C:/Users/mdzak/Documents/GitHub/cx3004/algorithm/image_rec/runs/detect/exp' #NEED TO BE CHANGED TO DIRECTORY OF DETECTED IMAGES
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

    cv2.imwrite('C:/Users/mdzak/Documents/GitHub/cx3004/algorithm/image_rec/result/result.png', combine) #CHANGE TO DIRECTORY WHERE STITCHED IMAGE IS SAVED
    cv2.imshow("Final Collage",combine)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detectbullseye():
    ROOT = FILE.parents[0]
    filename = str(uuid.uuid4())
    #filename = "data/images/" + filename + ".png
    save_dir = increment_path(Path("data/images") / "img", exist_ok=False)
    save_dir.mkdir(parents=True, exist_ok=True)
    #print(str(save_dir))
    img_file = str(save_dir)+'/'+filename+'.png'
    filepath = str(save_dir)
    cam_port = 'http://192.168.16.16/html/cam_pic_new.php'
    #cam_port = 0
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    if result:
        cv2.imwrite(img_file, image)
    id, box_size, angle= run_bullseye(filepath)
    if(box_size!=0):
        box_size = int(int(box_size)/1000) 
        box_size = 0.077*(box_size)*(box_size)-3.98*(box_size)+53.49

    if(angle != 0):
        print("raw angle is:", angle)
        if(angle == 300):
            angle = 0
        if(angle > 300):
            angle = (angle - 300)/9.65
            print("more than 300")
        elif(angle < 300):
            angle = -1*(31.1 - 0.104*(angle))
            print("less than 300")

    print("IMAGE DETECTED IS: ",id)
    print("DIST FROM ROBOT IS: ", int(box_size))
    print("ANGLE IS: ", int(angle))
    return id, int(box_size), int(angle)

