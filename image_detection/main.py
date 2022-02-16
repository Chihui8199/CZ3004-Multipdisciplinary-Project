from detect import *
from img_rec import *


id, dist, angle = detect()
print("IMAGE DETECTED IS: ",id)
print("DIST FROM ROBOT IS: ", dist)
print("ANGLE IS: ", angle)