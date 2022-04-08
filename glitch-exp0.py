# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 20:59:25 2022

@author: BenJammin
"""

import imageio
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage.util import random_noise
from skimage import feature

def show(img, cmap = None, saveas = None):
    sizes = np.shape(img)  
    fig = plt.figure()
    fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward = False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    
    if cmap is None:
        ax.imshow(img)
    else:
        ax.imshow(img, cmap = cmap)
        
    if saveas is not None:
        plt.savefig(saveas, dpi = 150) 
            
    #plt.close()
##################################################
# imgname = r"C:\Users\BenJammin\Pictures\2017-01\IMG_5204.JPG"
# raw = np.array(imageio.imread(imgname), dtype=float)
# raw = np.array(imageio.imread('prof-pic.jpg'), dtype=float)
raw = np.array(imageio.imread('glitchforge-raw.png'), dtype=float)
raw = raw/raw.max()
ogimg = random_noise(raw, mode='speckle', mean=0.1)

# Get edges from just 1 slice:
edg = feature.canny(ogimg[:,:,1], sigma=0.8)

# Mask
mask = ndi.gaussian_filter(1.0*(edg), 3) > 0.225

savename = 'GFR-tE2-s_5-sp1-flag'
show(mask, cmap = 'flag', saveas = savename)

# if True:
#     # Low pass original:
#     image = np.zeros(shape=ogimg.shape)
#     for ch in range(3):
#         # image[:,:,ch] = ndi.gaussian_filter(ogimg[:,:,ch], 1) * mask
#         image[:,:,ch] = ogimg[:,:,ch] 
#         image[:,:,ch]  *= 1.5*mask
    
    
    
#     show(image, saveas = 'creepy-mask-multiply')
