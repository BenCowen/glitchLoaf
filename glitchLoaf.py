# -*- coding: utf-8 -*-
"""
Glitch Lib

@author: Bunloaf23
"""
from glitch_this import ImageGlitcher
from PIL import Image
import numpy as np
import numpy.random as r

class bunGlitcher:
    def __init__(self):
        self.glitchThis = ImageGlitcher()
        
    def randU0(self):
        return r.rand() - 0.5
    def imresize(self, img, size):
        return np.array(Image.fromarray(img).resize(size, resample = Image.BICUBIC))
    
    def imSlice(self, imgArr, subset, subset_jitter = 0):
        # Take snippet for smaller gif
        xjitter = round( self.randU0() * subset_jitter * imgArr.shape[0] )
        yjitter = round( self.randU0() * subset_jitter * imgArr.shape[1] )
        rowmin = max(round(subset[0][0] * imgArr.shape[0]) + xjitter, 0)
        rowmax = min(round(subset[0][1] * imgArr.shape[0]) + yjitter, imgArr.shape[0])
        colmin = max(round(subset[1][0] * imgArr.shape[1]) - xjitter, 0)
        colmax = min(round(subset[1][1] * imgArr.shape[1]) - yjitter, imgArr.shape[1])
        return imgArr[rowmin:rowmax, colmin:colmax, :]
    
    def glitchThisImg(self, img, intensity, color = False):
        if type(img) is not Image.Image:
            img = Image.fromarray(img)
            
        return self.glitchThis.glitch_image(img, intensity, color_offset = color)
    
    def randomPatchSwap(self, img, nPatches, size_perc, filler_imgs = [], buffer = None):
        # TODO:
        # fix buffer so that the correct shapes get sliced out
        att = 'size' if (type(img) is Image.Image) else 'shape'
        imRows = getattr(img, att)[0]
        imCols = getattr(img, att)[1]
        
        if size_perc*min(imRows, imCols) < 1:
            return img
        
        
        get_rand = lambda MAX: r.randint(buffer, (1-buffer) * MAX)
        # Generate the patches
        for patch in range(nPatches):
            # Size:
            nrows = r.randint(0, size_perc*imRows)
            ncols = r.randint(0, size_perc*imCols)
            # Placement:
            row1 = get_rand(imRows)
            row2 = get_rand(imRows)
            col1 = get_rand(imCols)
            col2 = get_rand(imCols)
            z1   = r.randint(0, 3)
            z2   = r.randint(0, 3)
            # Set Filler:
            if len(filler_imgs) == 0:
                filler = img[row1:row1+nrows, col1:col1+ncols, z1]
            else:
                filler = self.imresize(filler_imgs[ r.randint(0,len(filler_imgs))], (nrows, ncols))
                
            try:
                img[row1:row1+nrows, col1:col1+ncols, z1] = img[row2:row2+nrows, col2:col2+ncols, z2]
            except ValueError:
                pass
            # Decide how to fill the 2nd patch:
            img[row2:row2+nrows, col2:col2+ncols, z2] = filler
            
        return img
            
            
            