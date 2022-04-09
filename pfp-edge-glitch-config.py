# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 14:23:49 2022

@author: BenJammin
"""


# Glitch Settings
rng_seed = 23

gtInt = {'style':'constant',
         'max'  : 0,
         'min'  : 0}

subSlice = {'limits': [[0,1],[0,1]],
            'jitter-style': 'constant',
            'max'  : 0,
            'min'  : 0}

occludes = {'num-style': 'constant',
            'num-max': 0,
            'num-min': 0,
            'size-style': 'updown-linear',
            'size-max': 0.4,
            'size-min': 0.2,
            'filler-imgs': [imageio.imread(r'imgs\ghoul-flame.png'),
                            imageio.imread(r'imgs\ghoul-example.jpg')]+
                            [imageio.imread(r'imgs\ghoul{}.png'.format(n)) for n in range(4)]}

resampleTo  = (1024, 1024)
edgeWidener = 0.25
cannySig = 2
edge_glitch_Intsy = 10
