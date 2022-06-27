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

glitch_config = loadSavedConfig('no-glitch')

glitch_config['bismuth'] = {#'startPoint': [centerPixel],
                           'direction': None,
                           'overlap': 0.25,
                           'patchSize': (0.2,0.2),
                           'growProb': 0.8,
                           'splitProb':0.1,
                           'n-splits': 2,
                           'random-new' : 0.033,
                           # Not Implemented:
                           'scaleRate':1,
                           'filler': None} #imgio.imread(r"C:\Users\BenJammin\Desktop\glitchLoaf\imgs\ghoul-flame.png"), }
 
height = 512
glitch_config['output-size'] = (height, int( height))
glitch_config['frame-select'] = {'beg':0, 'stepsize':1, 'end': 30}
###############################################################################
# Put your desired input and output here!
# input_path = 'imgs'
gs = ['CorruptedROM_021.png']
input_path = r"C:\Users\BenJammin\Desktop\glitchLoaf\imgs\killScreen"
add2save = '_NEW'

output_path = os.path.join('results')

for idx, fName in enumerate(gs):
    glitch_config['rng-seed'] = sum([ord(z) for z in fName])*23 # random number based on filename
    input_file  = os.path.join(input_path, fName)
    save_path   = os.path.join(output_path, fName.split('.')[0]) + add2save
        
    glitch_config['rng-seed'] = idx ** 2
    createGlitch(input_file, save_path, glitch_config)
        
        
        
    
