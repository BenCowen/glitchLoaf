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
from skimage.util import random_noise
from skimage import feature
from scipy import ndimage as ndi
import numpy.random as r
from Bismuth import BismuthDruse

# TODO: * preserve alpha channel in random occlusions
#       * replace slicing with comprehension or smart indexing
#       * probably want to restart cycle or something (instead of holding last frame)
#       * see unfinished glitch routines at the end of file
# TODO: better job of keeping original dynamic range
#       info = np.iinfo(self.img.dtype)

            
class bunGlitcher:
    def __init__(self, ogDataPath, output_path, frameSelect, resampleTo = None, glitchList = ['initBismuth']):
        self.ogDataPath = ogDataPath
        self.out_path   = output_path
        self.resampleTo = resampleTo
        
        # Analyze video vs image etc.
        self.frame_beg = frameSelect['beg']
        self.frame_end = frameSelect['end']
        self.frame_stepsize = frameSelect['stepsize']
        self._setupInputData(ogDataPath)
        
        # May be filled with gif frames:
        self.outputGif = []
        
        # Initialize persistent glitch objects:
        self.pGlitches = []
        for glitchName in glitchList:
            self.pGlitches.append( getattr(self, glitchName) )
            
    def _setupInputData(self, dataPath):
        ''' loads in the data to memory, initializes metadata'''
        if dataPath.endswith(('jpg','png')):
            self.ogDataType = 'image'
            self.ogData     = np.array(imageio.imread(dataPath), dtype=float)
            self.ogFrames   = 1
        elif dataPath.endswith(('gif','mp4','webp')):
            self.ogDataType = 'video'
            self.ogData     = imageio.get_reader(dataPath,  'ffmpeg')
            self.ogFrames   = self.ogData.count_frames()-1
        else:
            raise NotImplementedError('only jpg, png, mp4 tested; convert to one of those!')
        self.frames_done = 0
        self.frame_num   = self.frame_beg
        if (self.frame_end<0) or (self.frame_end > self.ogFrames):
            # Cap at the last frame (TODO: circular?)
            self.frame_end = self.ogFrames
    
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
            self.img = np.array(self.ogData.get_data(self.frame_num), dtype=float)
            
        # Data is always in [0,1] until very end.
        self.img = self.toNumpy01(self.img)
        
        # Resample to desired resolution:
        if self.resampleTo is not None:
            self.img = self.resizedSlices(self.img,
                                          self.resampleTo[0], self.resampleTo[1],
                                          [n for n in range(self.img.shape[-1])])
            self.clean_img = np.copy(self.img)
        
    def recordGifFrame(self):
        ''' save the current frame to the output Gif'''
        self.outputGif.append(self.img)
        
    def writeGIF(self):        
        print('writing gif - may take a while...')
        self.outputGif = [self._toPIL(frame) for frame in self.outputGif]
        imageio.mimsave('{}.gif'.format(self.out_path), self.outputGif)
        print('Done!')
        
    def writeFrame(self, cmap = None):
        print('writing JPG to "{}"...'.format(self.out_path))
        sizes = self.img.shape
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
        plt.close()
        print('Done!')
        
    ######################################
    # Quality of life subroutines:
    def _toPIL(self, inputs = None):
        ''' converts numpy array to PIL and takes care of float->uint8'''
        data = self.img if (inputs is None) else inputs
        if type(self.img) is not Image.Image:
            # Scale values back to uint8:
            data = self.toNumpy01(data)
            data *= 255
            # Finally, wrap with PIL:
            data = Image.fromarray(data.astype(np.uint8))
        if inputs is None:
            self.img = data
        else:
            return data
        
    def toNumpy01(self, data):
        data = np.array(data, dtype=float)
        # Make sure it's in [0, 1]
        data += data.min()
        data /= data.max()
        return data
    
    def randU0(self):
        ''' random uniform number in [-0.5, 0.5]'''
        return r.rand() - 0.5
    
    def imresize(self, data, size):
        ''' resamples `data` to given size'''
        return self.toNumpy01(self._toPIL(data).resize(size, resample = Image.BICUBIC))
    
    def resizedSlices(self, data, nrows, ncols, color_channels):
        ''' Resize the specified color channels of "data" '''
        filler = np.zeros((nrows, ncols, len(color_channels)))
        for cIdx, color_layer in enumerate(color_channels):
            filler[:,:,cIdx] = self.imresize(data[:,:,color_layer], 
                                            (ncols, nrows))
        return filler
    
    ######################################
    # Persistent Glitch Initialization
    # TODO: abstract persistent glitch class?... just make bismuth for now
    # TODO: config redux: 1 config per frame, and a gifConfig that
    #              generates subsequent ones with randomness
    def initBismuth(self, config = None):
        self.druse = BismuthDruse(self.clean_img, config)
        self.druse.newCrystal(config)
        
    def growBismuth(self):
        # TODO: have split_prob grow every frame? Make grow_prob
        #         and split_prob a property of each particular crystal
        # Determine which crystals to grow and/or split:
        # if a number is given then all crystals have same chance.
        
        # Grow selected crystals:
        self.druse.growCrystals()
        # Split crystals:
        self.druse.splitCrystals( n_splits = 2, sepAngle = 180)
        print('nBis={}'.format(len(self.druse)))
    def applyPersistentGlitches(self):
        self.img = self.druse.applyAllHistory(self.img)
        
    ######################################
    # Actual Glitch Effects
    def imSlice(self, subset, subset_jitter = 0, data = None):
        '''
        Take snippet of the data where `subset` gives 
          the percentages of each dimension to start/stop, 
          and subset_jitter specifies how much randomness to 
          use in the selection (0 gets the same subset every
          time).
        '''
        if data is None:
            imRows = self.img.shape[0]
            imCols = self.img.shape[1]
        else:
            imRows = data.shape[0]
            imCols = data.shape[1]
            
        # Random top-left corner: can't be below zero.
        xjitter = round( self.randU0() * subset_jitter * imRows )
        rowmin = max(round(subset[0][0] * imRows) + xjitter, 0)
        colmin = max(round(subset[1][0] * imCols) - xjitter, 0)
        #Random bottom-right corner: can't be bigger than data
        yjitter = round( self.randU0() * subset_jitter * imCols )
        rowmax = min(round(subset[0][1] * imRows) + yjitter, imRows)
        colmax = min(round(subset[1][1] * imCols) - yjitter, imCols)
        if data is None:
            self.img = self.img[rowmin:rowmax, colmin:colmax, :]
        else:
            return data[rowmin:rowmax, colmin:colmax, :]
    
    def glitchRect(self, data, direction = 'horz', 
                    maxBlockPerc = 0.2, intensity = 0.2):
        ''' 
         A block of rows/columns/etc. is shifted in bulk. The shift direction is
           perpendicular to the dimension of selection (`direction`). The size
           of the block is a percentage of the dimension to be blocked, and the
           intensity is a percentage of the dimension to be shifted along.
        '''
        # Specify horizontal or veritcal:
        blockDim = int(not (direction == 'horz'))
        shiftDim = int(    (direction == 'horz'))
        
        # Specify parameters and quit if non-visible
        blockLen = int((r.rand() * maxBlockPerc) * data.shape[blockDim])
        shiftLen = int((r.rand() *    intensity) * data.shape[shiftDim])
        if (blockLen < 1) or (shiftLen<1):
            return data
        # Express the block as percentage of the image size:
        blockStart     = r.randint(0, data.shape[blockDim] - blockLen)
        blockEnd       = blockStart + blockLen
        blockStartPerc = blockStart/data.shape[blockDim]
        blockEndPerc   =   blockEnd/data.shape[blockDim]
        blockSubset    = [blockStartPerc, blockEndPerc]
        
        # Extract the shifted subarray from the image:
        subset = [[], []]
        subset[blockDim] = blockSubset
        subset[shiftDim] = [0, 1]
        subArr = self.imSlice(subset, data=data)
        
        # Use Numpy ROLL to apply glitch:
        posneg   = 1 if (r.rand()>0.5) else -1
        subArr = np.roll(subArr, posneg * shiftLen, axis=shiftDim)
        
        # Now but the subArr back into the data:
        if direction == 'horz':
            data[blockStart:blockEnd, :] = subArr
        else:
            data[:, blockStart:blockEnd, :] = subArr
        
        return data
    
    def glitchImg(self, att='img', n_glitch=1, direction = 'both',
                  glitchIntensity = 0.2, glitchSize = 0.2):
        if not hasattr(self, att) or (n_glitch<1) or (glitchIntensity==0):
            return
        useDir = direction
        for glitch in range(n_glitch):
            if direction == 'both':
                useDir = 'horz' if (r.rand()>0.5) else 'vert'
            setattr(self,att, self.glitchRect(data=getattr(self, att),
                                       direction = useDir, 
                                       maxBlockPerc = glitchSize,
                                       intensity =glitchIntensity))
    
        
    def randomOcclusion(self, nPatches, size_perc,
                        filler_imgs = [], cChans_to_swap = 2):
        '''
        Random replacement of image patches 
            (by swapping or from filler imgs)
        '''
        imRows = self.img.shape[0]
        imCols = self.img.shape[1]
        
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
                filler = self.clean_img[row1:row1+nrows, col1:col1+ncols, z1]
            else:
                # If using filler data, need to reshape for the correct
                #  sized patch and also decide which color channels
                #  to replace and utilize.
                filler   = self.resizedSlices(filler_imgs[fillerSelect-1], nrows, ncols, z1)
            # Random chance to flip filler:
            if r.rand() > 0.5:
                filler = np.flip(filler, axis=r.randint(0,2))
                  
            # Fill patch 1 with patch 2,              
            self.img[row1:row1+nrows, col1:col1+ncols, z1] = self.clean_img[row2:row2+nrows, col2:col2+ncols, z2]
            # Fill patch 2 with filler:
            self.img[row2:row2+nrows, col2:col2+ncols, z2] = filler
            
            # Add on previous occlusions that have a hold time remaining:
            
    def thiccEdges(self, width = 0.333, cannySig=1):
        if width == 0:
            return
        imgsize = self.img.shape
        n_color_channels = min(3, imgsize[-1])
        edges = np.full((imgsize[0],imgsize[1],n_color_channels), 255)
        for channel in range(n_color_channels):
            edge_mask = feature.canny(self.img[:,:,channel], sigma = cannySig)
            # Smooth to thicken:
            edge_mask = ndi.gaussian_filter(1.0*(edge_mask), width) > 0
            # Edges are black
            edges[edge_mask, channel] = 0 
            
        self.edges = self.toNumpy01(edges)
        
    def randomColorSwap(self, prob = 0.5):
        if r.rand() > (1-prob):
            rand_color1 = r.randint(0,3)
            rand_color2 = r.randint(0,3)
            if not rand_color1 == rand_color2:
                temp = self.img[:,:, rand_color1]
                self.img[:,:, rand_color1] = self.img[:,:, rand_color2]
                self.img[:,:, rand_color2] = temp
            
    def multiplyEdgeMask(self):
        if not hasattr(self, 'edges'):
            print('tried multiplying edge mask but none available.')
            return
        n_color_channels = min(3, self.img.shape[-1])
        self.img[:,:,:n_color_channels] *= self.edges
        
    def addNoise(self, mode='speckle', intensity = 0.1):
        if mode is None:
            return
        self.img = 0.5*(self.img + random_noise(self.img, mode=mode))#, mean=mean)
        
    def blur(self, gWidth = 1):
        fw = int(gWidth)
        if fw==0:
            return
        # Blur the colors individually:
        n_color_channels = min(3, self.img.shape[-1])
        for channel in range(n_color_channels):
            #ndi.gaussian_filter(self.img[:,:,channel], gWidth)
            self.img[:,:,channel] = ndi.convolve(self.img[:,:,channel], np.full((fw, fw), 1/fw**2))
        # # Make sure result is still normalized...
        # self.img = self.toNumpy01(self.img)
        
    def stairCasingL1(self, L1_param = 0):
        ''' use L1 regularization to cause staircasing artifacts'''
        pass
    
    def smoothNLastFrames(self, N):
        ''' jointly process the last N frames of the output GIF'''
        pass
        
        
        
        
        
        
        