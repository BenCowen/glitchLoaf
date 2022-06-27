# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 08:22:20 2022

@author: BenJammin
"""

class PersistentGlitch(ABS):
    """Persistent glitch abstract class"""
    def __init__(self):
        # just making it exist
        self.FirstGrowth=True
        return
    def firstUpdate(self):
        return
    def update(self):
        if not self.FirstGrowth:
            return
        else:
            self.firstUpdate()
            return
        