# -*- coding: utf-8 -*-
"""
Glitch Lib

@author: Bunloaf23
@contact: benjamin.cowen.math@gmail.com
"""

# Misc
import imageio
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Processing
from glitch_this import ImageGlitcher
from skimage.util import random_noise
from skimage import feature
from scipy import ndimage as ndi
import numpy.random as r

# TODO: * preserve alpha channel in random occlusions
#       * replace slicing with comprehension or smart indexing
#       * probably want to restart cycle or something (instead of holding last frame)
#       * see unfinished glitch routines at the end of file
# TODO: better job of keeping original dynamic range
#       info = np.iinfo(self.img.dtype)
class bunGlitcher:
    def __init__(self, ogDataPath, output_path, frameSelect, resampleTo = None):
        self.glitchThis = ImageGlitcher()
        self.ogDataPath = ogDataPath
        self.out_path   = output_path
        self.resampleTo = resampleTo
        
        # Analyze video vs image etc.
        self.frame_beg = frameSelect['beg']
        self.frame_end = frameSelect['end']
        self.frame_stepsize = frameSelect['stepsize']
        self._setupInputData(ogDataPath, self.frame_beg)
        
        # May be filled with gif frames:
        self.outputGif = []
        
    def _setupInputData(self, dataPath, frame_beg = None):
        ''' loads in the data to memory, initializes metadata'''
        if dataPath.endswith(('jpg','png')):
            self.ogDataType = 'image'
            self.ogData     = np.array(imageio.imread(dataPath), dtype=float)
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
    def _toPIL(self, inputs = None):
        ''' converts numpy array to PIL and takes care of float->uint8'''
        if inputs is None:
            data = self.img
        if type(self.img) is not Image.Image:
            # Scale values back to uint8:
            data = self.ui8toF64(data)
            data *= 255
            # Finally, wrap with PIL:
            data = Image.fromarray(data.astype(np.uint8))
        if inputs is None:
            self.img = data
        else:
            return data
        
    def ui8toF64(self, data):
        return data.astype(np.float64) / 255 
    def _shape(self):
        ''' gets the shape tuple whether PIL or numpy array'''
        att = 'size' if (type(self.img) is Image.Image) else 'shape'
        return getattr(self.img, att)
    
    def randU0(self):
        ''' random uniform number in [-0.5, 0.5]'''
        return r.rand() - 0.5
    
    def imresize(self, data, size):
        ''' resamples `data` to given size'''
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
            self.img /= self.img.max()
        elif self.ogDataType == 'video':
            # Get next Frame
            self.frames_done += 1
            # For now, just hold onto the last frame
            self.frame_num    = min(self.frame_num + self.frame_stepsize,
                                    self.frame_end)
            self.reachedLastFrame = self.frame_num == self.frame_end
            # Retrieve data:
            self.img = self.ogData.get_data(self.frame_num)
        if self.resampleTo is not None:
            self.img = self.resizedSlices(self.img,
                                          self.resampleTo[0], self.resampleTo[1],
                                          [n for n in range(self._shape()[-1])])
        
    def recordGifFrame(self):
        ''' save the current frame to the output Gif'''
        self.outputGif.append(self.img)
        
    def writeGIF(self):        
        print('writing gif - may take a while...')
        self.outputGif = [self._toPIL(frame) for frame in self.outputGif]
            
        imageio.mimsave('{}.gif'.format(self.out_path), self.outputGif)
        print('Done!')
        
    def writeFrame(self, cmap = None):
        print('writing JPG...')
        sizes = self._shape()
        fig = plt.figure(dpi = 1200)
        fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward = False)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        
        if cmap is None:
            ax.imshow(self.img)
        else:
            ax.imshow(self.img, cmap = cmap)
            
        plt.savefig('{}.jpg'.format(self.out_path))
        #plt.savefig('{}.png'.format(self.out_path), dpi = 150) 
        plt.close()
        print('Done!')
        
    ######################################
    # Actual Glitch Effects
    def imSlice(self, subset, subset_jitter = 0):
        '''
        Take snippet of the data where `subset` gives 
          the percentages of each dimension to start/stop, 
          and subset_jitter specifies how much randomness to 
          use in the selection (0 gets the same subset every
          time).
        '''
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
        if intensity < 0.1:
            return
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
            fillerSelect = r.randint(0,len(filler_imgs)+1)
            # Set Filler:
            if fillerSelect == 0:
                # If no filler image data is provided, save
                #  the 'sister patch' for swapping.
                filler = self.img[row1:row1+nrows, col1:col1+ncols, z1]
            else:
                # If using filler data, need to reshape for the correct
                #  sized patch and also decide which color channels
                #  to replace and utilize.
                filler   = self.resizedSlices(filler_imgs[fillerSelect-1], nrows, ncols, z1)
                  
            # Fill patch 1 with patch 2,              
            # try:
            self.img[row1:row1+nrows, col1:col1+ncols, z1] = self.img[row2:row2+nrows, col2:col2+ncols, z2]
            # except ValueError:
            #     pass
            # Fill patch 2 with filler:
            self.img[row2:row2+nrows, col2:col2+ncols, z2] = filler
            
    def addNoise(self, mode='speckle', mean = 0.1):
        self.img = random_noise(self.img, mode=mode, mean=mean)
        
    def thiccEdges(self, width = 0.333):
        if width == 0:
            return
        n_color_channels = min(3, self._shape()[-1])
        edges = np.full(self._shape(), 255)
        for channel in range(n_color_channels):
            edge_mask = feature.canny(self.img[:,:,channel])
            # Smooth to thicken:
            edge_mask = ndi.gaussian_filter(1.0*(edge_mask), width) > 0
            # Edges are black
            edges[edge_mask, channel] = 0 
            
        self.img *= self.ui8toF64(edges)
        
    def stairCasingL1(self, L1_param = 0):
        ''' use L1 regularization to cause staircasing artifacts'''
        pass
    
    def smoothNLastFrames(self, N):
        ''' jointly process the last N frames of the output GIF'''
        pass
        
        
        
        
        
        
        
        
        