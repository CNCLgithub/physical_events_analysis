from IPython.display import clear_output, Image, display, HTML
import base64
import json
import os 
import subprocess
import sys
import numpy as np
import cv2
from matplotlib import pyplot as plt

# Where are the videos?
movie_folder=sys.argv[1] # give as input where the movies are 
base_movies=os.listdir(movie_folder)
base_movies=[mov for mov in base_movies if '.' not in mov]
print(base_movies)

# Preset dict for pixel change values
video_pixel_change=dict()

# which base movie are you going to look at? 
base_idx=sys.argv[2]
base_idx=int(base_idx)


probe_every=0.2 # probes occur every 200 ms

# Cycle through probe videos (just look at the first few for now)
for v in os.listdir(movie_folder+base_movies[base_idx]): 
    if '.mp4' in v: # if not a hidden file
        
        video_name=movie_folder+base_movies[base_idx]+'/'+ v
        print(video_name.split('/')[-1])
        
        bashCommand="ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate %s" % video_name
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE,text=True)
        output, error = process.communicate()
        frame_rate=np.int(output.split('/')[0])
        print('fps:',frame_rate)
        
        bashCommand="ffprobe -i %s -show_format" % video_name
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE,text=True)
        output, error = process.communicate()
        duration=float(output.split('duration=')[-1].split('\n')[0]) 
        print('duration (s):',duration)
        
        
        video = cv2.VideoCapture(video_name)

        _, frame = video.read()
        prevframe = frame    #First frame

        all_diffs=[]

        while(True):
            try:
                _, frame = video.read()
                nextframe = frame

                diff = cv2.absdiff(prevframe,nextframe)
                #cv2.imshow('video', diff)

                avg_diff=np.sum(diff)/(prevframe.shape[0]*prevframe.shape[1]*prevframe.shape[2]) # sum the absdiff
                all_diffs.append(avg_diff)

                prevframe = nextframe   

            except:
                
                break
                
        # reset / destroy
        cv2.destroyAllWindows()
        video.release()
        
        # ignore the countdown to the video which ends at 93 frames in 
        all_diffs=all_diffs[93:]
    
        #plt.figure()
        #plt.plot(np.arange(len(all_diffs)),all_diffs)
        
        # which probe was it?
        probe_num=video_name.split('/')[-1].split('_')[-1].split('.')[0]
        
        # calculate and visualize the probe start and end frames
        probe_start_frame=frame_rate*probe_every*np.int(probe_num)
        #plt.axvline(x=probe_start_frame,linestyle='dashed',color='black')
        #plt.axvline(x=probe_start_frame+frame_rate*probe_every,linestyle='dashed',color='black')
        
        probe_pixel_change=np.nanmean(all_diffs[round(probe_start_frame):round(probe_start_frame+frame_rate*probe_every)])
        print('Average pixel change during probe: %0.4f'%(probe_pixel_change)) 
        
        video_pixel_change[base_movies[base_idx]]=probe_pixel_change
        
        
with open('%s_pixel_changes.json' % base_movies[base_idx], 'w') as fp:
    json.dump(video_pixel_change, fp)
        
