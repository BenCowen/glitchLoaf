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

glitch_config = {}


glitch_config['frame-select'] = {'beg':0, 'stepsize':1, 'end':  10}

glitch_config['glitch-specs'] = {'int-style':'updown-linear',
                                 'int-max'  : 0,
                                 'int-min'  : 0,
                                 'num-style':'updown-linear',
                                 'num-max'  : 10,
                                 'num-min'  : 2,
                                 'sze-style':'updown-exp',
                                 'sze-max'  : 0.25,
                                 'sze-min'  : 0.05}

glitch_config['edge-glitches'] = {'int-style':'updown-exp',
                                  'int-max'  : 0.2,
                                  'int-min'  : 0.01,
                                  'num-style':'constant',
                                  'num-max'  : 10,
                                  'num-min'  : 2,
                                  'sze-style':'constant',
                                  'sze-max'  : 1/25, 
                                  'sze-min'  : 1/60,
                                  'thicc-style': 'constant',
                                  'thicc-max': 1,
                                  'thicc-min': 0,
                                  'cannySig':1}

asRat = 1
height = 512
glitch_config['output-size'] = (height, int(asRat * height))

glitch_config['blur'] = {'style':'constant',
                         'max':0,
                         'min':0}

# g_list = ['ghoul5344', 'ghoul5345', 'ghoul5346', 'ghoul6215', 'ghoul6216', 'ghoul6217']
# g_list = [r'C:\Users\BenJammin\Desktop\ghoul-stuff\my-ghouls\{}.png'.format(g) for g in g_list]
glitch_config['occludes'] = {'num-style': 'constant',
                             'num-max': 0,
                             'num-min': 0,
                             'size-style': 'updown-linear',
                             'size-max': 0.333,
                             'size-min': 0.1,
                             'filler-imgs': []}
                            
glitch_config['clrswp'] = {'style':'constant',
                           'max':0,
                           'min':0}

glitch_config['noise'] = {'style': 'constant',
                          'max':2,
                          'min':0,
                          'mode': 's&p'}

glitch_config['subSlice'] = {'limits': [[0,1],[0,1]],
                             'jitter-style': 'constant',
                             'max'  : 0,
                             'min'  : 0}

glitch_config['bismuth'] = None

###############################################################################
# Put your desired input and output here!
input_path = 'imgs'
gs = ['sun-img.jpg']

output_path = os.path.join('results')

for idx, fName in enumerate(gs):
    glitch_config['rng-seed'] = sum([ord(z) for z in fName])*23 # random number based on filename
    input_file  = os.path.join(input_path, fName)
    save_path   = os.path.join(output_path, fName.split('.')[0])
        
    glitch_config['rng-seed'] = idx ** 2
    createGlitch(input_file, save_path, glitch_config)
        
        
        
    
