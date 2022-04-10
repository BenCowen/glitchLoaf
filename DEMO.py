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
#
# TODO: need to somehow specify the algorithm itself...
#   i.e. a list of transforms to apply to each frame
#
# Be able to hang onto a corruption for multiple frames

# Import a video
import imageio
import numpy as np
import glitchLoaf as glitchLib

###############################################################################
# Configuration (settings)

############################
# Input/output paths:
# filename = 'girls-rolling.mp4'
# filename = 'mad-sign.jpg'
#filename = 'idol.jpg'
# filename = 'sj3280.png'
# filename = 'sgt-melon.png'
# filename = 'SJ-high5.gif'
# filename = 'prof-pic.jpg'
# filename = 'marty.png'
# filename = 'ghoul3.png'
# filename = 'sj8271.jpg'
# filename = 'sj5600.jpg'
# filename = 'lasjefas0.png'
# filename = 'SJ-high5.gif'
filename = 'gohan-dbz.mp4'
input_file  = r'imgs\{}'.format(filename)
output_path = r'results\{}'.format(filename.split('.')[0])

############################
# Glitch Settings
rng_seed = 23

frameSel = {'beg':0, 'stepsize':2, 'end': -1}

gtSpec = {'int-style':'updown-exp',
         'int-max'  : 0.25,
         'int-min'  : 0.05,
         'num-style':'updown-exp',
         'num-max'  : 10,
         'num-min'  : 2,
         'sze-style':'updown-linear',
         'sze-max'  : 1/10,
         'sze-min'  : 1/60}

edgeGT = {'int-style':'constant',
         'int-max'  : 0.05,
         'int-min'  : 0.01,
         'num-style':'constant',
         'num-max'  : 5,
         'num-min'  : 2,
         'sze-style':'constant',
         'sze-max'  : 1/20,
         'sze-min'  : 1/60,
         'edgeWidener': 0.15}

asRat = 1
height = 256
resampleTo  = (height, int(asRat * height))
cannySig = 1


blur = {'style':'updown-exp',
        'max':35,
        'min':0}

ghoul_ims  = [imageio.imread(r'imgs\ghoul-flame.png'), imageio.imread(r'imgs\ghoul-example.jpg')]
ghoul_ims += [imageio.imread(r'imgs\ghoul{}.png'.format(n)) for n in range(4)]
occludes = {'num-style': 'constant',
            'num-max': 0,
            'num-min': 0,
            'size-style': 'updown-linear',
            'size-max': 0.7,
            'size-min': 0.2,
            'filler-imgs': []}
                            
clrswp = {'style':'constant',
          'max':0,
          'min':0}

noise = {'style': 'updown-linear',
         'max':1,
         'min':0,
         'mode': None}#s&p'}

subSlice = {'limits': [[0,1],[0,1]],
            'jitter-style': 'constant',
            'max'  : 0,
            'min'  : 0}

# Not sure how to generalize the ramp book for "rule" scenario:
colorOffset = lambda f: bool(f > (0*frames2do))


###############################################################################
# From here on should be automated
loaf = glitchLib.bunGlitcher(input_file, output_path, frameSel, resampleTo)
    
# The actual gif loop happens outside the glitcher.
# Can put -1 if you want all frames; also caps to the last frame. TODO: cycle?
frames2do = max(1, int(np.ceil((loaf.frame_end-loaf.frame_beg)/loaf.frame_stepsize)))


#############
lin = np.linspace(0,1, int(frames2do/2))
ramps = {'increasing': np.linspace(0,1, int(frames2do)),
         'updown-linear': [n for n in lin] + [1] + [n for n in reversed(lin)],
         'updown-exp': [n**2 for n in lin] + [1] + [n**2 for n in reversed(lin)],
         'constant': [1]*frames2do}

# Glitch parameters:
glitchIntensity = lambda f:   gtSpec['int-min']  +    gtSpec['int-max'] * ramps[gtSpec['int-style']][f]
numGlitches     = lambda f:   gtSpec['num-min']  +    gtSpec['num-max'] * ramps[gtSpec['num-style']][f]
glitchSize      = lambda f:   gtSpec['sze-min']  +    gtSpec['sze-max'] * ramps[gtSpec['sze-style']][f]

edgeGlitchInsty = lambda f:   edgeGT['int-min']  +    edgeGT['int-max'] * ramps[edgeGT['int-style']][f]
edgeGlitchNum   = lambda f:   edgeGT['num-min']  +    edgeGT['num-max'] * ramps[edgeGT['num-style']][f]
edgeGlitchSize  = lambda f:   edgeGT['sze-min']  +    edgeGT['sze-max'] * ramps[edgeGT['sze-style']][f]

# Subset slice parameters:
subset_jitter  = lambda f: subSlice['min']  + subSlice['max'] * ramps[subSlice['jitter-style']][f]
# Patch swapping parameters:
size_perc = lambda f:  occludes['size-min'] + occludes['size-max'] * ramps[occludes['size-style']][f]
n_occlude = lambda f:  occludes['num-min']  + occludes['num-max']  * ramps[occludes['num-style']][f]
noiseMean = lambda f:         noise['min']  +    noise['max'] * ramps[noise['style']][f]
blurWidth = lambda f:          blur['min']  +     blur['max'] * ramps[blur['style']][f]
colorSwapProb = lambda f:          clrswp['min']  +     clrswp['max'] * ramps[clrswp['style']][f]

#######################################################################################
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
    
    nOcclde = int(n_occlude(frames_done))
    occSize = size_perc(frames_done)
    
    gtN       = int(numGlitches(frames_done))
    gtIntsy   = glitchIntensity(frames_done)
    gtChunkSz = glitchSize(frames_done)
    colrOff = False #Notimplemented anymore...
    
    noisAvg = noiseMean(frames_done)
    blurLvl = blurWidth(frames_done)
    
    edgeGlt     = edgeGlitchInsty(frames_done)
    edgeGtSz    = edgeGlitchSize(frames_done)
    nEdgeGlitch = edgeGlitchNum(frames_done)
    
    clrSwap = colorSwapProb(frames_done)
    #############################
    # Process the current frame
    # Go to next frame
    loaf.nextFrame()
    
    # Take jittered subset of the whole frame:
    loaf.imSlice(subSlice['limits'], subset_jitter = imSlice)
    
    # Extract and process edges before corrupting the image:
    loaf.thiccEdges(width = edgeGT['edgeWidener'],cannySig = cannySig)
    loaf.glitchImg(att='edges', n_glitch=nEdgeGlitch, direction = 'both',
                    glitchIntensity = edgeGlt, glitchSize = edgeGtSz)
    
    # Random color swapping:
    loaf.randomColorSwap(prob = clrSwap)
    # Random patch swapping and occlusion:
    loaf.randomOcclusion(nOcclde, occSize, filler_imgs = occludes['filler-imgs'])
    
    # Apply actual glitch:
    # TODO: color jitter replacement?
    loaf.glitchImg(att='img', n_glitch=gtN, direction = 'both',
                   glitchIntensity = gtIntsy, glitchSize = gtChunkSz)
    
    # Apply Glitch-This effects:
    # loaf.glitchImg(gtIntsy, color = colrOff)
    
    # Add Noise
    loaf.addNoise(mode=noise['mode'], intensity = noisAvg)
    
    # Blur colors:
    loaf.blur(gWidth = blurLvl)
    
    # Finally, multiply the original edges back in:
    loaf.multiplyEdgeMask()
    #############################
    # Save the frame:
    loaf.recordGifFrame()
    frames_done += 1
    
# Roll it up
if frames_done == 1:
    loaf.writeFrame()
else:
    loaf.writeGIF()






