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
import os
import imageio
from config_utils import loadSavedConfig
from glitchManager import createGlitch

###############################################################################
# Configuration (settings)

glitch_config = loadSavedConfig('last-ghoul')

glitch_config['bismuth'] = None

###############################################################################
# Put your desired input and output here!
input_path = 'imgs'
gs = ['sgt1.png']

output_path = os.path.join('results')

for idx, fName in enumerate(gs):
    glitch_config['rng-seed'] = sum([ord(z) for z in fName])*23 # random number based on filename
    input_file  = os.path.join(input_path, fName)
    save_path   = os.path.join(output_path, fName.split('.')[0])
        
    glitch_config['rng-seed'] = idx ** 2
    createGlitch(input_file, save_path, glitch_config)
        
        
        
    
