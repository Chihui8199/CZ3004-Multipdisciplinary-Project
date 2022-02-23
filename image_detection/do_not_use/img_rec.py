
from detect import *
from cv2 import *
import uuid
def run_model(filename):
    id, box_size, angle = run(source=ROOT / filename)
    return id, box_size, angle

def detect():
    ROOT = FILE.parents[0]
    filename = str(uuid.uuid4())
    #filename = "data/images/" + filename + ".png
    save_dir = increment_path(Path("data/images") / "img", exist_ok=False)
    save_dir.mkdir(parents=True, exist_ok=True)
    #print(str(save_dir))
    img_file = str(save_dir)+'/'+filename+'.png'
    filepath = str(save_dir)
    #cam_port = 'http://192.168.16.16/html/cam_pic_new.php'
    cam_port = 0
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    if result:
        cv2.imwrite(img_file, image)
    id, box_size, angle= run_model(filepath)
    if(box_size!=0):
        box_size = int(int(box_size)/1000) 
        box_size = 0.077*(box_size)*(box_size)-3.98*(box_size)+53.49
    return id, int(box_size), angle


