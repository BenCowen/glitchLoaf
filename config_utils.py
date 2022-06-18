# -*- coding: utf-8 -*-
"""
saved configs

@author: BenJammin
"""

def loadSavedConfig(config_ID):
    if config_ID == 'no-glitch':
        glitch_config = {}


        glitch_config['frame-select'] = {'beg':0, 'stepsize':1, 'end':  1}

        glitch_config['glitch-specs'] = {'int-style':'updown-linear',
                                         'int-max'  : 0,#0.333,
                                         'int-min'  : 0,#0.12,
                                         'num-style':'updown-linear',
                                         'num-max'  : 0,#20,
                                         'num-min'  : 0,#2,
                                         'sze-style':'updown-linear',
                                         'sze-max'  : 0,#1/20,
                                         'sze-min'  : 0,}#0.05}

        glitch_config['edge-glitches'] = {'int-style':'updown-linear',
                                          'int-max'  : 0,#0.1,
                                          'int-min'  : 0,#0.01,
                                          'num-style':'constant',
                                          'num-max'  : 0,#25,
                                          'num-min'  : 0,#2,
                                          'sze-style':'constant',
                                          'sze-max'  : 0,#1/25, 
                                          'sze-min'  : 0,#1/60,
                                          'thicc-style': 'constant',
                                          'thicc-max': 0,#0.05,
                                          'thicc-min': 0,#0.025,
                                          'cannySig':1}

        asRat = 1
        height = 512
        glitch_config['output-size'] = (height, int(asRat * height))

        glitch_config['blur'] = {'style':'updown-linear',
                                 'max':0,#10,
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
                                  'max':0,
                                  'min':0,
                                  'mode': None}#'s&p'}

        glitch_config['subSlice'] = {'limits': [[0,1],[0,1]],
                                     'jitter-style': 'constant',
                                     'max'  : 0,
                                     'min'  : 0}
        glitch_config['bismuth'] = None
    elif config_ID == 'last-ghoul':
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

    return glitch_config