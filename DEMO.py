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
from glitchManager import createGlitch

###############################################################################
# Configuration (settings)

glitch_config = {}


glitch_config['frame-select'] = {'beg':0, 'stepsize':1, 'end':  15}

glitch_config['glitch-specs'] = {'int-style':'updown-linear',
                                 'int-max'  : 0.333,
                                 'int-min'  : 0.12,
                                 'num-style':'updown-linear',
                                 'num-max'  : 20,
                                 'num-min'  : 2,
                                 'sze-style':'updown-linear',
                                 'sze-max'  : 1/20,
                                 'sze-min'  : 0.05}

glitch_config['edge-glitches'] = {'int-style':'updown-linear',
                                  'int-max'  : 0.1,
                                  'int-min'  : 0.01,
                                  'num-style':'constant',
                                  'num-max'  : 25,
                                  'num-min'  : 2,
                                  'sze-style':'constant',
                                  'sze-max'  : 1/25, 
                                  'sze-min'  : 1/60,
                                  'thicc-style': 'constant',
                                  'thicc-max': 0.05,
                                  'thicc-min': 0.025,
                                  'cannySig':1}

asRat = 1
height = 512
glitch_config['output-size'] = (height, int(asRat * height))

glitch_config['blur'] = {'style':'updown-linear',
                         'max':10,
                         'min':0}

# ghoul_ims  = [imageio.imread(r'imgs\ghoul-flame.png'), imageio.imread(r'imgs\ghoul-example.jpg')]
# ghoul_ims += [imageio.imread(r'imgs\ghoul{}.png'.format(n)) for n in range(4)]
glitch_config['occludes'] = {'num-style': 'constant',
                             'num-max': 0,
                             'num-min': 0,
                             'size-style': 'constant',
                             'size-max': 0.333,
                             'size-min': 0.2,
                             'filler-imgs': []}
                            
glitch_config['clrswp'] = {'style':'constant',
                           'max':0,
                           'min':0}

glitch_config['noise'] = {'style': 'decreasing',
                          'max':1,
                          'min':0,
                          'mode': 's&p'}

glitch_config['subSlice'] = {'limits': [[0,1],[0,1]],
                             'jitter-style': 'constant',
                             'max'  : 0,
                             'min'  : 0}

# Not sure how to generalize the ramp book for "rule" scenario:
glitch_config['colorOffset'] = lambda f: bool(f > (0*frames2do))


###############################################################################
# Put your desired input and output here!
gs = ['g1', 'g2','g3','g4','g5','g6','g7','g8','long-live']
for idx, fName in enumerate(gs):
    input_file  = r'imgs\ghouls\{}.jpg'.format(fName)
    output_path = r'imgs\ghouls\glitched\{}'.format(fName)
        
    glitch_config['rng-seed'] = idx ** 2
    createGlitch(input_file, output_path, glitch_config)
        
        
        
    
