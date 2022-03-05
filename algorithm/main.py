from image_rec.img_rec import conf_level, detect, stitch_save
from image_rec.img_rec import stitch
import time
conf_obj = conf_level()

a,b,c,d,e = detect(conf_obj)
#stitch_save()
stitch()