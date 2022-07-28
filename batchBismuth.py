# -*- coding: utf-8 -*-
"""
Source Quantity Experiment
@author: BenLoaf23
@date 07/28/2022
"""
import os
import time
import imageio
from config_utils import loadSavedConfig
from glitchManager import createGlitch
import glob
import imageio as imgio
import numpy as np

###############################################################################
# Glitch Configuration (does not change over time)
nFrames = 50
height = 256

glitch_config = loadSavedConfig(None)#'last-ghoul')
glitch_config['save-list-frame'] = True
glitch_config['process-fft'] = False


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
glitch_config['output-size'] = (height, int( height))
glitch_config['frame-select'] = {'beg':0, 'stepsize':1, 'end': nFrames}
baseOutputPath = r"C:\Users\Ben Jammin\killscreen_src_vol2\_OUTPUT_"

###############################################################################
# Data Configuration
# Collect all available data (ignoring .zip subdir's...)
srcPathList = glob.glob(r"C:\Users\Ben Jammin\killscreen_src_vol2\**\*.png", recursive=True)
nSrc = len(srcPathList)

# Preload and resize all files:
loadSt = time.time()
srcList = [imgio.imread(imgPath) for imgPath in srcPathList]
print('Time to load {} imgs = {}s'.format(nSrc, time.time()-loadSt))

# Number of auxiliary files
nAuxList = [2, 10, 20, 200]

initialSt = time.time()
expnum = 0
totalEst = len(srcList) * len(nAuxList)
timeList =[[] for n in nAuxList]
for idx, motherFile in enumerate(srcList):
    for auxIdx, nAux in enumerate(nAuxList):
        # Output config:
        motherID = srcPathList[idx].split('\\')[-1].split('.')[0]
        save_path = os.path.join(baseOutputPath, '{}_nAux{}'.format(motherID, nAux))
        
        # Aux files:
        glitch_config['filler-imgs'] =  [srcList[np.random.randint(nSrc)] for n in range(nAux)]
        
        # RNGOD
        glitch_config['rng-seed'] = expnum ** 2
        
        # Execute:
        st = time.time()
        createGlitch(motherFile, save_path, glitch_config)
        timeList[auxIdx].append(time.time()-st)
        print('Exp {}/{}; total time={}hrs'.format(expnum, totalEst, (time.time()-initialSt)/60**2))
        expnum += 1











