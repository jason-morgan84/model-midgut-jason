import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import matplotlib.animation as animation

import shapely.geometry as sg
import shapely
import matplotlib.pyplot as plt
import math



figure, axes = plt.subplots()
axes.set_aspect( 1 )
#axes.set_axis_off()
plt.xlim(0, 20)
plt.ylim(0, 20)
plt.title( 'Packing Test' )
defaultheight=2
defaultwidthratio=0.5
sizevariation = 0.25
number_of_ellipses=100
height=[]
width=[]
rotation=[]
for i in range(number_of_ellipses):
    height.append(np.random.normal(defaultheight,defaultheight*sizevariation))
    width.append(np.random.normal(defaultheight*defaultwidthratio,defaultheight*defaultwidthratio*sizevariation))
    rotation.append(np.random.random()*90)

y_range=[0,10]
x_range=[0,15]  

#print(height)
#print(width)

#list of elipses center_x,center_y,short_axis,long_axis,orienation
EllipsisList = []

"""
Ellipses.append()
            self.artist = mpatches.Ellipse(
                xy = tuple(self.Position.AsList()),
                width = self.Morphology.Size.X,
                height = self.Morphology.Size.Y,
                fill = True,edgecolor=self.Format.LineColour,
                facecolor = self.Format.FillColour,
                picker = True,
                zorder = 5) """



plt.show()
