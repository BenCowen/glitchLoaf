# -*- coding: utf-8 -*-
"""
Frame by frame video glitcher with output to GIF.

@author: BenLoaf23
"""

#TODO: work on single-img manipulation (pfp + mds)
# Whole loop maybe needs to be moved into glitchLoaf;
#    or make a new class that owns a glitchLoaf and
#    automates parameters/config
#
# use an actual config format

# Import a video
import numpy as np
import glitchLoaf as glitchLib

###############################################################################
# Configuration (settings)

############################
# Input/output paths:
# input_file = r'imgs\girls-rolling.mp4'
filename = 'mad-sign.jpg'
input_file  = r'imgs\{}'.format(filename)
output_path = r'results\{}'.format(filename.split('.')[0])

############################
# Glitch Settings
rng_seed = 23

gtInt = {'style':'constant',
         'max'  : 4,
         'min'  : 0.1}

subSlice = {'limits': [[0,1],[0,1]],
            'jitter-style': 'constant',
            'max'  : 0,
            'min'  : 0}

occludes = {'num-style': 'constant',
            'num-max': 10,
            'num-min': 0,
            'size-style': 'updown-linear',
            'size-max': 0.1,
            'size-min': 0,
            'filler-imgs': []}#imageio.imread(r'imgs\ghoul-flame.png')]}

# FRAME RANGE:

# girls-rolling:
#frameSel = {'beg':150, 'stepsize':2, 'end':260}

# single img:
frameSel = {'beg':0, 'stepsize':1, 'end':5}

###############################################################################
# From here on should be automated
loaf = glitchLib.bunGlitcher(input_file, output_path, frameSel)
    
# The actual gif loop happens outside the glitcher.
# Can put -1 if you want all frames; also caps to the last frame. TODO: cycle?
frames2do = max(1, int(np.ceil((frameSel['end']-frameSel['beg'])/frameSel['stepsize'])))


#############
lin = np.linspace(0,1, int(frames2do/2))
ramps = {'updown-linear': [n for n in lin] + [1] + [n for n in reversed(lin)],
         'constant': [1]*frames2do}

# Glitch-this parameters:
glitchIntensity = lambda f:   gtInt['min']  +    gtInt['max'] * ramps[gtInt['style']][f]
# Subset slice parameters:
subset_jitter  = lambda f: subSlice['min']  + subSlice['max'] * ramps[subSlice['jitter-style']][f]
# Patch swapping parameters:
size_perc = lambda f:  occludes['size-min'] + occludes['size-max'] * ramps[occludes['size-style']][f]
n_occlude = lambda f:  occludes['num-min']  + occludes['num-max']  * ramps[occludes['num-style']][f]

# Not sure how to generalize the ramp book for "rule" scenario:
colorOffset = lambda f: bool(f > (0.75*frames2do))

#############################
np.random.seed(rng_seed)
frames_done = 0
while True:
    #############################
    # Keep track of frames     
    # TODO: randomly go backward N frames (deja vu)
    isDone = (frames_done>=frames2do)
    if isDone:
        break
    print('Processing frame {}/{}...'.format(frames_done+1, frames2do))
    #############################
    # Change parameters as
    #  w/frame number.
    imSlice = subset_jitter(frames_done)
    occSize = size_perc(frames_done)
    gtIntsy = glitchIntensity(frames_done)
    colrOff = colorOffset(frames_done)
    nOcclde = n_occlude(frames_done)
    
    #############################
    # Process the current frame
    # Go to next frame
    loaf.nextFrame()
    
    # Take jittered subset of the whole frame:
    loaf.imSlice(subSlice['limits'], imSlice)
    
    # Random patch swapping and occlusion:
    loaf.randomOcclusion(nOcclde, occSize, filler_imgs = occludes['filler-imgs'])
    
    # Apply Glitch-This effects:
    loaf.glitchThisImg(gtIntsy, color = colrOff)
    
    # Save the frame:
    loaf.recordGifFrame()
    frames_done += 1
    
# Roll it up
if frames_done == 1:
    loaf.writeFrame()
else:
    loaf.writeGIF()






