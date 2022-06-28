# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 14:37:06 2022

@author: BenJammin
"""

import numpy as np
        
class BismuthCrystal():
    """ one crystal that can grow a tail etc."""
    def __init__(self, startPoint, filler, direction, growProb,
                 splitProb, overlap=0.5, do_edge=False, patchSize=None):
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
        self.jump_size =  np.sqrt(self.nrows**2 + self.ncols**2) * (1-overlap)
        self.do_edge   = do_edge
        self.patchSize = patchSize
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
        rowFin     = min(rowSt + self.nrows, image.shape[0]-1)
        nrows      = max(0, rowFin - rowSt)
        
        colCenter  = self.pos_hist[idx][1]
        halfWidth  = round(self.ncols/2)
        colSt      = max(0, colCenter - halfWidth)
        colFin     = min(colSt + self.ncols, image.shape[1]-1)
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
            image[rowSt:rowFin, colSt, :]  *= 0
            image[rowSt:rowFin, colFin, :] *= 0
            image[rowSt, colSt:colFin, :]  *= 0
            image[rowFin, colSt:colFin, :] *= 0
        # print('success={}'.format(success))
        return image, success
    
    
class BismuthDruse:
    """ A collection of Bismuth Crystals"""
    def __init__(self, origin_config, split_config):
        # Filler is always taken from original if not provided.
        self.crystals = []
        self.do_edges = origin_config['highlight-edges']
        self.base_config  = origin_config
        self.split_config = split_config
        
    def __len__(self):
        return len(self.crystals)
    
    def newCrystal(self, filler, config=None, fromSplit = False, startPoint=None, 
                   direction = None, lastPatchSize=None):
        if config is None:
            config = self.base_config
            
        if startPoint is None:
            startPoint = config['startPoint']
            
        #----------------------------
        # Parse patchSize
        if 'patchSizeFactor' in config:
            patchSize = tuple([config['patchSizeFactor'] * x for x in lastPatchSize])
        else:
            patchSize = config['patchSize']
            
        #----------------------------
        # Parse direction
        if 'directionStyle' in config:
            if config['directionStyle']=='cart':
                # Random along-axis direction:
                direction = self.rotateVec((0,1), np.random.randint(0,3)*90)
        elif direction is None:
            direction = self.randomUnitVector()  if (config['direction'] is  None) else config['direction']
            
        #----------------------------
        # Parse filler
        patch = self.getPatch(filler, startPoint, patchSize)
         
        #----------------------------
        # Create the new Crystal:   
        self.crystals.append( BismuthCrystal(startPoint, patch, 
                                             direction, config['growProb'],
                                             config['splitProb'], config['overlap'],
                                             do_edge=self.do_edges, patchSize=patchSize))
        self.crystals[-1].fromSplit = fromSplit
        
    def splitCrystals(self, filler, n_splits = 2, sepAngle = 180):
        for crystal_idx in range(len(self.crystals)):
            if np.random.rand() < self.crystals[crystal_idx].splitProb:
                self.crystals[crystal_idx].growProb = 0
                crystal = self.crystals[crystal_idx]
                # Determine parent config: (make this a tree struct?)
                if crystal.fromSplit:
                    parent_config = self.split_config
                else:
                    parent_config = self.base_config
                n_splits = n_splits if (parent_config['n-splits'] is None)  else parent_config['n-splits']
                sepAngle = n_splits if (parent_config['sep-angle'] is None) else parent_config['sep-angle']
                
                # Now derive N new crystals from the last one
                angles = np.linspace(-sepAngle, sepAngle, n_splits)
                for angle in angles:
                    new_dir = self.rotateVec(crystal.direction, angle)
                    new_pos = crystal.grow(override_dir = new_dir, return_new = True)
                    self.split_config['startPoint'] = new_pos
                    self.split_config['direction'] = new_dir
                    self.newCrystal(filler, config=self.split_config, fromSplit=True, 
                                    lastPatchSize=crystal.patchSize)
        
    def growCrystals(self):
        for crystal in self.crystals:
            if np.random.rand() < crystal.growProb:
                crystal.grow()
            
    def applyAllHistory(self, image):
        
        for cIdx, crystal in enumerate(self.crystals):
            for idx in range(len(crystal)):
                image, success = crystal.draw(image, idx)
                if not success:
                    crystal.growProb=0
                    break
            
                    
        return image
    
    def getPatch(self, src, center, patchSize, r=1): 
        x, y = center[0], center[1]
        imRows = src.shape[0]
        imCols = src.shape[1]
        patchPixels = np.array([round(patchSize[0] * imRows), round(patchSize[1] * imCols)])
        halfPat     = np.array([round(patchPixels[0] / 2), round(patchPixels[1] /2)])
  
        rowSt  = max(x-int(r*halfPat[0]), 0)
        rowFin = min(x+int(r*halfPat[0]), imRows-1)
        colSt  = max(y-int(r*halfPat[1]), 0)
        colFin = min(y+int(r*halfPat[1]), imCols-1)
        patch  = src[rowSt:rowFin, colSt:colFin,:]
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
        # Assume input is in degrees/convert to radians:
       theta *= (np.pi/180)
       newX = vec[0]*np.cos(theta) - vec[1] * np.sin(theta)
       newY = vec[0]*np.sin(theta) + vec[1] * np.cos(theta)
       return (newX, newY)