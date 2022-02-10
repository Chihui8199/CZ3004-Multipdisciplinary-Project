from numpy import angle
from detect import *
from cv2 import *
import uuid
def run_model(filename):
    id, box_size, angle = run(source=ROOT / filename)
    return id, box_size, angle

def detect():
    ROOT = FILE.parents[0]
    filename = str(uuid.uuid4())
    #filename = "data/images/" + filename + ".png"
    save_dir = increment_path(Path("data/images") / "img", exist_ok=False)
    save_dir.mkdir(parents=True, exist_ok=True)
    #print(str(save_dir))
    img_file = str(save_dir)+'/'+filename+'.png'
    filepath = str(save_dir)
    cam_port = 0
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    if result:
        cv2.imwrite(img_file, image)
    id, box_size, angle= run_model(filepath)
    return id, box_size, angle

id,box_size,angle = detect()
print("IMAGE DETECTED IS: ",id)
print("BOX SIZE IS: ", box_size)
print("ANGLE IS: ", angle)

