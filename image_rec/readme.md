## Source Code Information for Algo Team  
1. All python files required to run EXCEPT main.py, it is for my own testing purpose
2. Algo team need to only worry about img_rec.py
3. 5 functions to be used is detect(),stitch(), start_async(), stop_async(), numdetected(), ignore the rest of functions
4. detect() function flow: take photo -> save photo in data/images -> run model on said photo -> if detected draw bounding box and save in  runs/detect/exp -> return object_name ,object_id, dist, angle
5. stitch() function combines images in runs/detect/exp and save in result, to be used at the end of run
6. start_async() starts a thread that does image recognition every 5 seconds
7. stop_async() stops the thread started by start_async()
8. numdetected() returns the number of different images detected so far
9. requirements.txt, all dependencies needed

## Directory Information  
1. Raw Image taken by Pi Camera and stored in data/images
2. If any of 30 images is detected, save image with bounding box in runs/detect/exp
3. All images in runs/detect/exp have to be deleted before every run to ensure a fresh start
4. Stitched image of all detected images is stored in result
