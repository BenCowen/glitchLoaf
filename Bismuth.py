# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 14:37:06 2022

@author: BenJammin
"""

        
class BismuthCrystal():
    """ one crystal that can grow a tail, split into N branches, etc."""
    def __init__(self, startPoint, filler, direction, overlap=0.5):
        """
            startPoint: pixel coordinate for the center of the first filler
            filler: the data used to grow the crystal
            direction: a unit vector describing the direction to grow in
            overlap: the stepsize of growth in terms of a percentage of the filler size
        """
        self.pos_hist  = [startPoint]
        self.direction = direction
        self.overlap   = overlap
        self.filler    = filler
    def __len__(self):
        return len(self.pos_hist)
    
    def grow(self):
        """ generate a new position, add to pos_hist"""
        # TODO
    def draw(self, idx, image):
        """ paint filler onto an image"""
        nrows, ncols = self.filler
        
        rowCenter  = self.pos_hist[idx][0]
        halfHeight = round(nrows/2)
        rowSt      =  rowCenter - halfHeight
        
        colCenter = self.pos_hist[idx][1]
        halfWid   = round(ncols/2)
        colSt     =  colCenter - halfWidth
        
        image[rowSt:rowSt+nrows, colSt:colSt+ncols, :] = filler
        return image
    
    
def BismuthDruse():
    """ A collection of Bismuth Crystals"""
    def __init__(self, startPointList, directionList, overlap, scaleRate):
        # need to be able to change some of the inputs for different crystals...
        self.crystals = []
        for startPoint, direction in zip(startPointList, directinList):
            self.crystals.append( BismuthCrystal(startPoint, filler, direction,...) )
    def splitCrystal(self, crystal_idx, n_splits = 2, separation_angle = 90):
        crystal = self.crystals.pop(crystal_idx)
        # Now derive N new crystals from the last one
        print('TODO')
    def applyAllHistory(self, random_select = 1):
        for crystal in self.crystals:
            if np.random.rand() > random_select:
                continue # TODO: somehow initialize this at new-frame time so it doesnt grow either?...
            for idx in range(len(crystal)):
                crystal.draw(idx)
                
   @staticmethod
   def renorm(self, X):
       if isinstance(X, list):
           X = np.array(X)
       return X/X.sum()
   @staticmethod
   def randomUnitVector(self, N):
       ''' generate a random vector on unit N-ball'''
       random_direction = renorm(np.random.rand(N) - 0.5)
       return np.array(random_direction)
   
def bismuthGrowth(self, startPoint, startDirection = None, patchSize = [0.25,0.25],
                 length = 25, max_jump = 0.1, direction_consistency = 1, distSamplerName='normal',
                 do_edge=True, filler = None):
   '''
   Take a block of pixels and slide it around, leaving a trail of itself behind.
   direction_consistency: how crazy the trail is
       If direction_consistency == 0, direction of trail is random.
       If direction_consistency == 1, direction is unchanging after 1st random pull.
   
   distSamplerName: name of numpy.random module from which to sample distances.
   '''
   
   def getFiller(src, x,y, r=1, filler=None):
       patch = src[x-int(r*halfPat[0]):x+int(r*halfPat[0]),
                   y-int(r*halfPat[1]):y+int(r*halfPat[1]),:]
       if filler is not None:
           patch = self.imresize(filler, (patch.shape[1],patch.shape[0]))
       if filler.shape[-1]==4:
           patch = patch[:,:,:3]
       return patch
   
   imRows = self.img.shape[0]
   imCols = self.img.shape[1]
   patchPixels =  np.array([round(patchSize[0] * imRows), round(patchSize[1] * imCols)])
   halfPat     =  np.array([round(patchPixels[0] / 2), round(patchPixels[1] /2)])
   
   # Initialize stepsizer
   sampleStepsize = lambda: getattr(np.random, distSamplerName)()
   
   # TODO: randomize starting position
   lastDir = randomUnitVector(2) if startDirection is None else renorm(startDirection)
   x = round(imRows * startPoint[0])
   y = round(imCols * startPoint[1])
   
   lastRow = x
   lastCol = y
   src = np.copy(self.img)
       
   for fram in range(length):
       try:
           # Calculate next block location:
           lastDir = direction_consistency * renorm(lastDir) + (1-direction_consistency)*randomUnitVector(2)
           offset = (sampleStepsize() * max_jump * patchPixels) * renorm(lastDir)
           lastRow += round(offset[0])
           lastCol += round(offset[1])
           
           lastRow = max(0, lastRow)
           lastCol = max(0, lastCol)
           # TODO: randomize size...?...
           r = 0.5 + np.random.rand() * 0.25
           # Add the block to the new location:
           self.img[lastRow-int(halfPat[0]*r):lastRow+int(halfPat[0]*r), 
                    lastCol-int(halfPat[1]*r):lastCol+int(halfPat[1]*r),:] = getFiller(src, x,y,r, filler)
           # Add edge
           if do_edge:
               self.img[lastRow-halfPat[0]:lastRow+halfPat[0], lastCol-halfPat[1], :] *= 0
               self.img[lastRow-halfPat[0]:lastRow+halfPat[0], lastCol+halfPat[1], :] *= 0
               self.img[lastRow-halfPat[0], lastCol-halfPat[1]:lastCol+halfPat[1], :] *= 0
               self.img[lastRow+halfPat[0], lastCol-halfPat[1]:lastCol+halfPat[1], :] *= 0
       except Exception as e:
           print('failed bismuth as frame {}/{}'.format(fram, length))
           print(e)
           return
