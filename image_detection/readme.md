## Source Code Information for Algo Team  
1. All python files required to run, algo team need to only worry about img_rec.py
2. Ignore all code except img_rec.py
3. 2 functions to be used is detect() and stitch(), ignore the rest of functions
4. object_name ,object_id, dist, angle = detect(), detect() function returns 4 values
5. stitch() function combines images in runs/detect/exp and save in result, to be used at the end of run
6. requirements.txt, all dependencies needed

## Directory Information  
1. Raw Image taken by Pi Camera and stored in data/images
2. If any of 30 images is detected, save image with bounding box in runs/detect/exp
3. All images in runs/detect/exp have to be deleted before every run to ensure a fresh start
4. Stitched image of all detected images is stored in result
