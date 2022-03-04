from image_rec.img_rec import conf_level, detect
from image_rec.img_rec import stitch
import time
conf_obj = conf_level()

id, id_num, dist, angle,conf = detect(conf_obj)
print("Confidence level 1: ", conf)

id, id_num, dist, angle,conf = detect(conf_obj)
print("Confidence level 1: ", conf)



stitch()