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
import time
import imageio
from config_utils import loadSavedConfig
from glitchManager import createGlitch

###############################################################################
# Configuration (settings)

glitch_config = loadSavedConfig(None)#'last-ghoul')
glitch_config['save-list-frame'] = True
glitch_config['process-fft'] = False

fillerCodes=[n for n in range(1,29)]
fillerCodes.pop(7)
fillerCodes.pop(18)
prep = r"C:\Users\BenJammin\Desktop\glitchLoaf\imgs\killScreen\CorruptedROM_"
glitch_config['filler-imgs'] = ['{}{:03d}.png'.format(prep, code) for code in fillerCodes]

glitch_config['bismuth'] = {'new-origin-prob':0.5,
                            'origin-config':
                                {'startPoint': 'center',
                                  'directionStyle': 'cart',
                                  'overlap': 0.05,
                                  'patchSize':(0.175,0.175),
                                  'growProb':1,
                                  'splitProb':.25,
                                  'surviveSplit':True,
                                  'n-splits':2,
                                  'highlight-edges':False,
                                  'sep-angle':180
                                  },
                            'split-config':
                                {'overlap': 0.125,
                                  'patchSizeFactor':0.25,
                                  'growProb': 1,
                                  'splitProb':0.1,
                                  'surviveSplit':False,
                                  'n-splits':2,
                                  'sep-angle':180,
                                  }
                            }
height = 512
glitch_config['output-size'] = (height, int( height))
glitch_config['frame-select'] = {'beg':0, 'stepsize':1, 'end': 50}
###############################################################################
# Put your desired input and output here!
# input_path = 'imgs'
gs = ['CorruptedROM_029.png']
input_path = r"C:\Users\BenJammin\Desktop\glitchLoaf\imgs\killScreen"
add2save = 'composite-cartesian'

output_path = os.path.join('results')

st=time.time()
for idx, fName in enumerate(gs):
    glitch_config['rng-seed'] = sum([ord(z) for z in fName])*32 # random number based on filename
    input_file  = os.path.join(input_path, fName)
    save_path   = os.path.join(output_path, fName.split('.')[0]) + add2save
        
    glitch_config['rng-seed'] = idx ** 2
    createGlitch(input_file, save_path, glitch_config)
        
        
print('time: {}s'.format(time.time()-st))
    
