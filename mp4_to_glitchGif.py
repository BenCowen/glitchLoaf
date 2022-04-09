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
movie_file = r'imgs\girls-rolling.mp4'

# Prayer to the RNGod
rng_seed = 23

# Frame range
frame_beg      =  150
frame_stepsize = 2
frame_end      = 260 # -1 for all
loaf = glitchLib.bunGlitcher(movie_file, frame_beg, frame_end, frame_stepsize)
    
if ( frame_end < 0) or (frame_end > loaf.ogFrames):
    frame_end = loaf.ogFrames
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
    
    # Go to next frame
    loaf.nextFrame()
    
    # Take jittered subset:
    loaf.imSlice(subset, subset_jitter(frames_done))
    # Random patch swapping and occlusion:
    loaf.randomOcclusion(nPatches, size_perc(frames_done), 
                         filler_imgs = filler_imgs)
    # Apply Glitch-This effects:
    loaf.glitchThisImg(glitchIntensity(frames_done), 
                       color = colorOffset(frames_done))
    # Save the frame:
    loaf.recordGifFrame()
    
# Roll it up
loaf.writeGIF(output_path)






