# -*- coding: utf-8 -*-
"""
Frame by frame video glitcher with output to GIF.

@author: BenLoaf23
"""

# Import a video
import imageio
import numpy as np
import glitchLoaf as glitchLib
#############################
# Configuration (settings)

# Go ahead and load the mp4:
movie_file = 'girls-rolling.mp4'
vid = imageio.get_reader(movie_file,  'ffmpeg')

# Prayer to the RNGod
rng_seed = 23

# Frame range
frame_beg      =  150
frame_stepsize = 2
frame_end      = 260 # -1 for all
# Check last frame:
n_frame = vid.count_frames()
if ( frame_end < 0) or (frame_end > n_frame):
    frame_end = n_frame
frames2do = np.ceil((frame_end-frame_beg)/frame_stepsize)
#############
lin = np.linspace(0,1, int(frames2do/2))
frame_ramp = [n for n in lin] + [1] + [n for n in reversed(lin)] 

# Glitch-this parameters:
glitchIntensity = lambda f: 0.1 + 2 * frame_ramp[f]
colorOffset = lambda f: bool(f > (0.75*frames2do))

# Subset jitter parameters:

subset = [[0.2,0.5],[0.3,.7]]#[[1/3, 2/3], [1/5, 1/2]]
subset_jitter = lambda f: 1/60 * frame_ramp[f]

# Patch swapping parameters:
nPatches = 10
size_perc = lambda f:  0.2 * frame_ramp[f]
filler_imgs = [imageio.imread(r'imgs\ghoul-flame.png')]
 
# Output GIF path:
output_path = 'rollgif-new.gif'


#############################

    
frames_done = 0
frames_todo = (frame_end- frame_beg) // frame_stepsize

# TEMP:
loaf = glitchLib.bunGlitcher()
    
gif_list = []
frame_num = frame_beg
while True:
    print('Done with {}/{} frames'.format(frames_done, frames_todo))
    # Increment
    frames_done += 1
    frame_num   += frame_stepsize
    isDone = frame_num >= frame_end
    if isDone:
        break
    
    # Load in data
    image = vid.get_data(frame_num)
    
    # Process
    image = loaf.imSlice(image, subset, 
                               subset_jitter(frames_done))
    image = loaf.randomPatchSwap(image, nPatches,
                                       size_perc(frames_done), 
                                       filler_imgs = filler_imgs)
    image = loaf.glitchThisImg(image, 
                                     glitchIntensity(frames_done), 
                                     color = colorOffset(frames_done))
    gif_list.append( image )
    
# Roll it up
print('writing gif - may take a sec...')
imageio.mimsave(output_path, gif_list)
print('Done!')

# For a better glitcher:
# class Glitcher:
#     def __init__(self, parameters, glitchFcn = None, seed=23):
        
#         if glitchFcn is None: # use default: glitch-this
#             glitchThis = ImageGlitcher()
#             # If default isn't given then
#             #  parameters need to match Glitch-This interface:
#             self.glitchFrame = lambda img: glitchThis.glitch_image(img, **parameters)
            
#     def glitchImg(self, img):
#         return self.glitchrame(img)
#     def glitchVideo(self,img):
# def GenericGlitchImage(img):
    
    