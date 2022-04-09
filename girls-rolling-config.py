# -*- coding: utf-8 -*-
"""
girls-rolling config

@author: Bunloaf23
"""


gtInt = {'style':'updown-linear',
         'max'  : 2,
         'min'  : 0.1}

subSlice = {'limits': [[0.2,0.5],[0.3,.7]],
            'jitter-style': 'updown-linear',
            'max'  : 1/60,
            'min'  : 0}

occludes = {'num-style': 'constant',
            'num-max': 10,
            'num-min': 0,
            'size-style': 'updown-linear',
            'size-max': 0.2,
            'size-min': 0,
            'filler-imgs': [imageio.imread(r'imgs\ghoul-flame.png')]}

# FRAME RANGE:

# girls-rolling:
frameSel = {'beg':150, 'stepsize':2, 'end':260}