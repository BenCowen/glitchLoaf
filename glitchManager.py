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
    
    ##########################################################
    # Create the glitcher object:            
    loaf = glitchLib.bunGlitcher(input_file, output_path, glitch_config['frame-select'], 
                                 glitch_config['output-size'], process_fft=glitch_config['process-fft'])
        
    # Initialize frame loop parameters
    if loaf.frame_end == 1 and glitch_config['frame-select']['end']>1:
        frames2do = glitch_config['frame-select']['end']
    else:
        frames2do = max(1, int(np.ceil((loaf.frame_end-loaf.frame_beg)/loaf.frame_stepsize)))
    
    ##########################################################
    # Setup parameter functions to change with frames:
    # TODO: abstract this to a schedule class and avoid 50 lines of config specification
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
    subSlice       = glitch_config['subSlice']
    subset_jitter  = lambda f: subSlice['min']  + subSlice['max'] * ramps[subSlice['jitter-style']][f]
    
    # Patch swapping parameters:
    occludes  = glitch_config['occludes']
    noise     = glitch_config['noise']
    blur      = glitch_config['blur']
    clrswp    = glitch_config['clrswp']
    size_perc = lambda f:  occludes['size-min'] + occludes['size-max'] * ramps[occludes['size-style']][f]
    n_occlude = lambda f:  occludes['num-min']  + occludes['num-max']  * ramps[occludes['num-style']][f]
    noiseMean = lambda f:         noise['min']  +    noise['max'] * ramps[noise['style']][f]
    blurWidth = lambda f:          blur['min']  +     blur['max'] * ramps[blur['style']][f]
    colorSwapProb = lambda f:    clrswp['min']  +   clrswp['max'] * ramps[clrswp['style']][f]
    bisConfig = glitch_config['bismuth'] # shorthand
    
    #######################################################################################
    # Initialize filler imagines if only image paths were given
    if (len(glitch_config['filler-imgs'])>0) and (isinstance(glitch_config['filler-imgs'][0], str)):
        filler_images = [imgio.imread(imgPath) for imgPath in glitch_config['filler-imgs']]
    else:
        filler_images = glitch_config['filler-imgs']
    if filler_images is not None:
        # TODO: breaking occlude behavior for the sake of bismuth right now:
        for idx, I in enumerate(filler_images):
            filler_images[idx] = loaf.resizedSlices(I,
                                          loaf.resampleTo[0], loaf.resampleTo[1],
                                          [n for n in range(I.shape[-1])])
        nFiller = len(filler_images)
        randomFiller = lambda: filler_images[np.random.randint(0,nFiller)]
    else:
        randomFiller = None
        
        
    #######################################################################################
    np.random.seed(glitch_config['rng-seed'])
    frames_done = 0
    
    #------------------------------------------
    
    
    while True:
        ##########################################################
        # Keep track of frames     
        # TODO: randomly go backward N frames (deja vu effect)
        isDone = (frames_done>=frames2do)
        if isDone:
            break
        print('Processing frame {}/{}...'.format(frames_done+1, frames2do))
        
        ##########################################################
        # Call parameter functions to actually fill in values
        imSlice = subset_jitter(frames_done)
        
        nOcclde = int(n_occlude(frames_done))
        occSize = size_perc(frames_done)
        
        gtN       = int(numGlitches(frames_done))
        gtIntsy   = glitchIntensity(frames_done)
        gtChunkSz = glitchSize(frames_done)
        colrOff   = False #Notimplemented anymore...
        
        noisAvg = noiseMean(frames_done)
        blurLvl = blurWidth(frames_done)
        
        edgeGlt     = edgeGlitchInsty(frames_done)
        edgeGtSz    = edgeGlitchSize(frames_done)
        nEdgeGlitch = int(edgeGlitchNum(frames_done))
        edgeThc     = edgeThiccner(frames_done)
        edgeThc     = 0 if (edgeThc<0.01) else edgeThc
        
        clrSwap = colorSwapProb(frames_done)
        
        ##########################################################
        # Process the the next frame
        loaf.nextFrame()
        
        # TODO: really need to loop through a list of methods (requested glitches)
        #        whose order is in config instead of listing out here...
        if bisConfig is not None:
            # Select a filler:
            if frames_done<1 or (np.random.rand()<bisConfig['new-origin-prob']):
                oConfig = bisConfig['origin-config']
                if frames_done<1:
                    nrows, ncols = loaf.img.shape[0],loaf.img.shape[1]
                    oConfig['startPoint'] = (nrows//2, ncols//2)
                    loaf.initBismuth(randomFiller(), oConfig, bisConfig['split-config'])
                else:
                    oConfig['startPoint'] = (np.random.randint(0,loaf.clean_img.shape[0]), np.random.randint(0,loaf.clean_img.shape[1]))
                    loaf.druse.newCrystal(randomFiller(), oConfig)
                    
            loaf.growBismuth(randomFiller())
            loaf.applyPersistentGlitches()
        
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
        if ('save-list-frame' in glitch_config) and glitch_config['save-list-frame']:
            loaf.writeFrame()
    