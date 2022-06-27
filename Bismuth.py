# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 14:37:06 2022

@author: BenJammin
"""

import numpy as np
        
class BismuthCrystal():
    """ one crystal that can grow a tail etc."""
    def __init__(self, startPoint, filler, direction, growProb,
                 splitProb, overlap=0.5, do_edge=False):
        """
            startPoint: pixel coordinate for the center of the first filler
            filler: the data used to grow the crystal
            direction: a unit vector describing the direction to grow in
            overlap: the stepsize of growth in terms of a percentage of the filler size
        """
        self.pos_hist  = [startPoint]
        self.direction = direction
        self.filler    = filler
        self.nrows, self.ncols = self.filler.shape[0], self.filler.shape[1]
        self.growProb  = growProb
        self.splitProb = splitProb
        self.jump_size =  np.sqrt(self.nrows**2 + self.ncols**2) * overlap
        self.do_edge = do_edge
        
    def __len__(self):
        return len(self.pos_hist)
    
    def grow(self, override_dir = None, return_new = False):
        """ generate a new position, add to pos_hist"""
        direction  = self.direction if (override_dir is None) else override_dir
        translation = tuple([self.jump_size * x for x in direction])
        new_center = tuple([int(x1+x2) for x1,x2 in zip(self.pos_hist[-1], translation)])
        if return_new:
            return new_center
        else:
            self.pos_hist.append( new_center )
        
    def draw(self, image, idx):
        """ paint filler onto an image"""
        rowCenter  = self.pos_hist[idx][0]
        halfHeight = round(self.nrows/2)
        rowSt      = max(0, rowCenter - halfHeight)
        rowFin     = min(rowSt + self.nrows, image.shape[0])
        nrows      = max(0, rowFin - rowSt)
        
        colCenter  = self.pos_hist[idx][1]
        halfWidth  = round(self.ncols/2)
        colSt      = max(0, colCenter - halfWidth)
        colFin     = min(colSt + self.ncols, image.shape[1])
        ncols      = max(0, colFin - colSt)
        
        # print('-------------')
        # print('rowSt{} -- len{}'.format(rowSt, nrows + rowSt))
        # print('colSt{} -- len{}'.format(colSt, ncols + colSt))
        # print('Filler size:{}'.format(self.filler.shape))
        # print('image size:{}'.format(image.shape))
        if nrows<=0 or ncols<=0:
            return image, False
        else:
            success =  True
        try:
            image[rowSt:rowFin, colSt:colFin, :] = self.filler[:nrows, :ncols, :]
        except ValueError:
            print('hi')
        # Add edge
        if self.do_edge:
            image[lastRow-halfPat[0]:lastRow+halfPat[0], lastCol-halfPat[1], :] *= 0
            image[lastRow-halfPat[0]:lastRow+halfPat[0], lastCol+halfPat[1], :] *= 0
            image[lastRow-halfPat[0], lastCol-halfPat[1]:lastCol+halfPat[1], :] *= 0
            image[lastRow+halfPat[0], lastCol-halfPat[1]:lastCol+halfPat[1], :] *= 0
        # print('success={}'.format(success))
        return image, success
    
    
class BismuthDruse:
    """ A collection of Bismuth Crystals"""
    def __init__(self, image, config):
        # Filler is always taken from original if not provided.
        self.image    = image 
        self.crystals = []
        self.base_config = config
        
    def __len__(self):
        return len(self.crystals)
    def newCrystal(self, config=None, startPoint=None, direction = None):
        if config is None:
            config = self.base_config
        if startPoint is None:
            startPoint = config['startPoint']
        if direction is None:
            direction = self.randomUnitVector()  if (config['direction'] is  None) else config['direction']
        filler = config['filler']
        # If no aux filler is provided, take the corresponding chunk from given img
        if filler is None:
            filler = self.getPatch(self.image, startPoint, config['patchSize'])
            
        self.crystals.append( BismuthCrystal(startPoint, filler, 
                                             direction, config['growProb'],
                                             config['splitProb'], config['overlap']) )
        
    def splitCrystals(self, n_splits = 2, sepAngle = 180):
        n_splits = n_splits if (self.base_config['n-splits'] is None) else self.base_config['n-splits']
        #TODO: how change config for new splits?
        for crystal_idx in range(len(self.crystals)):
            if np.random.rand() < self.crystals[crystal_idx].splitProb:
                self.crystals[crystal_idx].growProb = 0
                crystal = self.crystals[crystal_idx]
                # Now derive N new crystals from the last one
                angles = np.linspace(-sepAngle, sepAngle, n_splits)
                for angle in angles:
                    new_dir = self.rotateVec(crystal.direction, angle)
                    new_pos = crystal.grow(override_dir = new_dir, return_new = True)
                    filler  = self.getPatch(self.image, new_pos, self.base_config['patchSize'])
                    # TODO: assumes 50% overlap
                    self.newCrystal(startPoint=new_pos, direction=new_dir)
        
    def growCrystals(self):
        for crystal in self.crystals:
            if np.random.rand() < crystal.growProb:
                crystal.grow()
            
    def applyAllHistory(self, image):
        
        for cIdx, crystal in enumerate(self.crystals):
            for idx in range(len(crystal)):
                image, success = crystal.draw(image, idx)
                if not success:
                    #TODO: need to remove somehow...
                    break
            
                    
        return image
    
    def getPatch(self, src, center, patchSize, r=1): 
       x, y = center[0], center[1]
       imRows = src.shape[0]
       imCols = src.shape[1]
       patchPixels = np.array([round(patchSize[0] * imRows), round(patchSize[1] * imCols)])
       halfPat     = np.array([round(patchPixels[0] / 2), round(patchPixels[1] /2)])
  
       patch = src[x-int(r*halfPat[0]):x+int(r*halfPat[0]),
                   y-int(r*halfPat[1]):y+int(r*halfPat[1]),:]
       # if patch.shape[-1]==4:
       #     patch = patch[:,:,:3]
       return patch
   
    # @staticmethod
    def renorm(self, X):
       if isinstance(X, list):
           X = np.array(X)
       return X/X.sum()
    # @staticmethod
    def randomUnitVector(self, N = 2):
       ''' generate a random vector on unit N-ball'''
       random_direction = self.renorm(np.random.rand(N) - 0.5)
       return np.array(random_direction)
    # @staticmethod
    def rotateVec(self, vec, theta=90):
       newX = vec[0]*np.cos(theta) - vec[1] * np.sin(theta)
       newY = vec[0]*np.sin(theta) + vec[1] * np.cos(theta)
       return (newX, newY)