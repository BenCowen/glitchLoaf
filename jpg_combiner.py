# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 20:05:31 2022

@author: BenJammin
"""
import matplotlib.pyplot as plt
import imageio as imgio
import numpy as np

g_list = ['ghoul5344', 'ghoul5345', 'ghoul5346', 'ghoul6215', 'ghoul6216', 'ghoul6217', 'ghoul6184']
g_list = [r'C:\Users\BenJammin\Desktop\ghoul-stuff\my-ghouls\{}.png'.format(g) for g in g_list]

n = len(g_list)

for idx,imgPath in enumerate(g_list):
    loaded = np.array(imgio.imread(imgPath), dtype=float)
    if idx==0:
        s = loaded
    elif imgPath.split('\\')[-1] == 'ghoul6184.png':
        s += 4.5*loaded
        
    else:
        s += loaded

s/=255        
s /= n

fig = plt.figure(dpi = 1200)
fig.set_size_inches(1. * loaded.shape[0] / loaded.shape[1], 1, 
                    forward = False)
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
ax.imshow(s)
plt.savefig('strong-peg.jpg')