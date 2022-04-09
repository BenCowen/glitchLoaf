# -*- coding: utf-8 -*-
"""
Glitch Lib

@author: Bunloaf23
@contact: benjamin.cowen.math@gmail.com
"""

import imageio

from glitch_this import ImageGlitcher
from PIL import Image
import numpy as np
import numpy.random as r

# TODO: * preserve alpha channel in random occlusions
#       * replace slicing with comprehension or smart indexing
#       * probably want to restart cycle or something (instead of holding last frame)
#       * see unfinished glitch routines at the end of file
class bunGlitcher:
    def __init__(self, ogDataPath, frame_beg = 0, 
                       frame_end=-1, frame_stepsize = 1):
        self.glitchThis = ImageGlitcher()
        self.ogDataPath = ogDataPath
        
        # Analyze video vs image etc.
        self.frame_beg = frame_beg
        self.frame_end = frame_end
        self.frame_stepsize = frame_stepsize
        self._setupInputData(ogDataPath, self.frame_beg)
        
        # May be filled with gif frames:
        self.outputGif = []
        
    def _setupInputData(self, dataPath, frame_beg = None):
        if dataPath.endswith(('jpg','png')):
            self.ogDataType = 'image'
            self.ogData     = np.array(imageio.imread('glitchforge-raw.png'), dtype=float)
            self.ogFrames   = 1
        elif dataPath.endswith('mp4'):
            self.ogDataType = 'video'
            self.ogData     = imageio.get_reader(dataPath,  'ffmpeg')
            self.ogFrames   = self.ogData._meta['nframes']
        else:
            raise NotImplementedError('only jpg, png, mp4 tested; convert to one of those!')
        self.frames_done = 0
        self.frame_num   = frame_beg
    ######################################
    # Quality of life subroutines:
    def _toPIL(self):
        if type(self.img) is not Image.Image:
            self.img = Image.fromarray(self.img)
    def _shape(self):
        att = 'size' if (type(self.img) is Image.Image) else 'shape'
        return getattr(self.img, att)
    def randU0(self):
        return r.rand() - 0.5
    def imresize(self, data, size):
        return np.array(Image.fromarray(data).resize(size, resample = Image.BICUBIC))
    def resizedSlices(self, data, nrows, ncols, color_channels):
        ''' Resize the specified color channels of "data" '''
        filler     = np.zeros((nrows, ncols, len(color_channels)))
        for cIdx, color_layer in enumerate(color_channels):
            filler[:,:,cIdx] = self.imresize(data[:,:,color_layer], 
                                            (ncols, nrows))
        return filler
    
    ######################################
    # Data Management
    def nextFrame(self):
        '''
        If the input type is just an image, then that is used
        over and over to make a gif from an image. If the input
        type is a video, config parameters are used to get the
        next frame.
        '''
        if self.ogDataType == 'image':
            self.img = self.ogData
        elif self.ogDataType == 'video':
            # Get next Frame
            self.frames_done += 1
            # For now, just hold onto the last frame
            self.frame_num    = min(self.frame_num + self.frame_stepsize,
                                    self.frame_end)
            self.reachedLastFrame = self.frame_num == self.frame_end
            # Retrieve data:
            self.img = self.ogData.get_data(self.frame_num)
        
    def recordGifFrame(self):
        ''' save the current frame to the output Gif'''
        self.outputGif.append(self.img)
    def writeGIF(self, outputFileName = None):
        
        print('writing gif - may take a sec...')
        imageio.mimsave(outputFileName, self.outputGif)
        print('Done!')
        
    ######################################
    # Actual Glitch Effects
    def imSlice(self, subset, subset_jitter = 0):
        '''Take snippet for smaller gif'''
        imRows = self._shape()[0]
        imCols = self._shape()[1]
        # Random top-left corner: can't be below zero.
        xjitter = round( self.randU0() * subset_jitter * imRows )
        rowmin = max(round(subset[0][0] * imRows) + xjitter, 0)
        colmin = max(round(subset[1][0] * imCols) - xjitter, 0)
        #Random bottom-right corner: can't be bigger than data
        yjitter = round( self.randU0() * subset_jitter * imCols )
        rowmax = min(round(subset[0][1] * imRows) + yjitter, imRows)
        colmax = min(round(subset[1][1] * imCols) - yjitter, imCols)
        self.img = self.img[rowmin:rowmax, colmin:colmax, :]
    
    def glitchThisImg(self, intensity, color = False):
        '''Invoke Glitch-This'''
        self._toPIL()
        self.img = self.glitchThis.glitch_image(self.img,
                                                intensity,
                                                color_offset = color)
    
    def randomOcclusion(self, nPatches, size_perc,
                        filler_imgs = [], cChans_to_swap = 2):
        '''
        Random replacement of image patches 
            (by swapping or from filler imgs)
        '''
        imRows = self._shape()[0]
        imCols = self._shape()[1]
        
        # Max patch size must be >= 1 pixel in both directions.
        if size_perc*min(imRows, imCols) < 1:
            return
        
        # Generate the patches
        for patch in range(nPatches):
            # Size:
            nrows = r.randint(1, size_perc*imRows)
            ncols = r.randint(1, size_perc*imCols)
            # Placement:
            row1 = r.randint(imRows - nrows)
            row2 = r.randint(imRows - nrows)
            col1 = r.randint(imCols - ncols)
            col2 = r.randint(imCols - ncols)
            z1   = r.randint(0, 3, 2)
            z2   = r.randint(0, 3, 2)
            # Set Filler:
            if len(filler_imgs) == 0:
                # If no filler image data is provided, save
                #  the 'sister patch' for swapping.
                filler = self.img[row1:row1+nrows, col1:col1+ncols, z1]
            else:
                # If using filler data, need to reshape for the correct
                #  sized patch and also decide which color channels
                #  to replace and utilize.
                imselect = r.randint(0, len(filler_imgs))
                filler   = self.resizedSlices(filler_imgs[imselect], nrows, ncols, z1)
                  
            # Fill patch 1 with patch 2,              
            # try:
            self.img[row1:row1+nrows, col1:col1+ncols, z1] = self.img[row2:row2+nrows, col2:col2+ncols, z2]
            # except ValueError:
            #     pass
            # Fill patch 2 with filler:
            self.img[row2:row2+nrows, col2:col2+ncols, z2] = filler
            
        def stairCasingL1(self, L1_param = 0):
            ''' use L1 regularization to cause staircasing artifacts'''
            pass
        def smoothNLastFrames(self, N):
            ''' jointly process the last N frames of the output GIF'''
            pass