# -*- coding: utf-8 -*-
"""
Created on Mon May 23 15:07:12 2022

@author: BenJammin
"""


import numpy as np
import glitchLoaf as glitchLib
import imageio as imgio


###############################################################################
# From here on should be automated
def createGlitch(input_file, output_path, glitch_config):
    
    loaf = glitchLib.bunGlitcher(input_file, output_path, glitch_config['frame-select'], glitch_config['output-size'])
        
    # The actual gif loop happens outside the glitcher.
    # Can put -1 if you want all frames; also caps to the last frame. TODO: cycle?
    if loaf.frame_end == 1 and glitch_config['frame-select']['end']>1:
        frames2do = glitch_config['frame-select']['end']
    else:
        frames2do = max(1, int(np.ceil((loaf.frame_end-loaf.frame_beg)/loaf.frame_stepsize)))
    
    # TODO:
    # Not sure how to generalize the ramp book for "rule" scenario:
    glitch_config['colorOffset'] = lambda f: bool(f > (0*frames2do))
    
    #############
    lin = np.linspace(0,1, int(frames2do/2))
    ramps = {'increasing': np.linspace(0,1, int(frames2do)),
             'decreasing': [n for n in reversed(np.linspace(0,1,int(frames2do)))],
             'increasing-exp': [n**3 for n in np.linspace(0,1, int(frames2do))],
             'updown-linear': [n for n in lin] + [1] + [n for n in reversed(lin)],
             'updown-exp': [n**2 for n in lin] + [1] + [n**2 for n in reversed(lin)],
             'constant': [1]*frames2do}
    
    # Glitch parameters:
    gtSpec = glitch_config['glitch-specs']
    glitchIntensity = lambda f:   gtSpec['int-min']  +    gtSpec['int-max'] * ramps[gtSpec['int-style']][f]
    numGlitches     = lambda f:   gtSpec['num-min']  +    gtSpec['num-max'] * ramps[gtSpec['num-style']][f]
    glitchSize      = lambda f:   gtSpec['sze-min']  +    gtSpec['sze-max'] * ramps[gtSpec['sze-style']][f]
    
    edgeGT = glitch_config['edge-glitches']
    edgeGlitchInsty = lambda f:   edgeGT['int-min']  +    edgeGT['int-max'] * ramps[edgeGT['int-style']][f]
    edgeGlitchNum   = lambda f:   edgeGT['num-min']  +    edgeGT['num-max'] * ramps[edgeGT['num-style']][f]
    edgeGlitchSize  = lambda f:   edgeGT['sze-min']  +    edgeGT['sze-max'] * ramps[edgeGT['sze-style']][f]
    edgeThiccner    = lambda f:   edgeGT['thicc-min']  +    edgeGT['thicc-max'] * ramps[edgeGT['thicc-style']][f]
    
    # Subset slice parameters:
    subSlice = glitch_config['subSlice']
    subset_jitter  = lambda f: subSlice['min']  + subSlice['max'] * ramps[subSlice['jitter-style']][f]
    # Patch swapping parameters:
    occludes = glitch_config['occludes']
    noise = glitch_config['noise']
    blur = glitch_config['blur']
    clrswp = glitch_config['clrswp']
    size_perc = lambda f:  occludes['size-min'] + occludes['size-max'] * ramps[occludes['size-style']][f]
    n_occlude = lambda f:  occludes['num-min']  + occludes['num-max']  * ramps[occludes['num-style']][f]
    noiseMean = lambda f:         noise['min']  +    noise['max'] * ramps[noise['style']][f]
    blurWidth = lambda f:          blur['min']  +     blur['max'] * ramps[blur['style']][f]
    colorSwapProb = lambda f:          clrswp['min']  +     clrswp['max'] * ramps[clrswp['style']][f]
    
    
    #######################################################################################
    if (len(occludes['filler-imgs'])>0) and (isinstance(occludes['filler-imgs'][0], str)):
        filler_images = [imgio.imread(imgPath) for imgPath in occludes['filler-imgs']]
    else:
        filler_images = occludes['filler-imgs']
        
    #######################################################################################
    np.random.seed(glitch_config['rng-seed'])
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
        nEdgeGlitch = int(edgeGlitchNum(frames_done))
        edgeThc     = edgeThiccner(frames_done)
        edgeThc     = 0 if (edgeThc<0.01) else edgeThc
        
        clrSwap = colorSwapProb(frames_done)
        #############################
        # Process the current frame
        # Go to next frame
        loaf.nextFrame()
        
        # Bismuth growth
        if glitch_config['bismuth']  is not None:
            patchSize = 0.2
            length = 20
            direction_consistency = 0.75
            max_jump = 0.1
            distSamplerName = 'normal'
            loaf.bismuthGrowth(patchSize = patchSize, length = length, max_jump =max_jump, 
                                direction_consistency = direction_consistency,
                                distSamplerName=distSamplerName)
        
        # Take jittered subset of the whole frame:
        loaf.imSlice(subSlice['limits'], subset_jitter = imSlice)
        
        # Extract and process edges before corrupting the image:
        loaf.thiccEdges(width = edgeThc,cannySig = glitch_config['edge-glitches']['cannySig'])
        loaf.glitchImg(att='edges', n_glitch=nEdgeGlitch, direction = 'both',
                        glitchIntensity = edgeGlt, glitchSize = edgeGtSz)
        
        # Random color swapping:
        loaf.randomColorSwap(prob = clrSwap)
        
        # Apply actual glitch:
        # TODO: color jitter replacement?
        loaf.glitchImg(att='img', n_glitch=gtN, direction = 'both',
                       glitchIntensity = gtIntsy, glitchSize = gtChunkSz)
        
        # Random patch swapping and occlusion:
        loaf.randomOcclusion(nOcclde, occSize, filler_imgs = filler_images)
        
        # Blur colors:
        loaf.blur(gWidth = blurLvl)
        
        # Finally, multiply the original edges back in:
        loaf.multiplyEdgeMask()
        
        # Add Noise
        loaf.addNoise(mode=noise['mode'], intensity = noisAvg)
        #############################
        # Save the frame:
        loaf.recordGifFrame()
        frames_done += 1
        
    # Roll it up
    if frames_done == 1:
        loaf.writeFrame()
    else:
        loaf.writeGIF()
    