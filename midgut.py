import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


class CellTypes:
    def __init__(self, name, number, shape, x, y, size, orientation=None):
        self.name=name
        self.starting_number = number
        self.starting_shape = shape
        self.starting_position=[x,y]
        if shape == "circle":
            self.starting_radius = size
        elif shape == "rectangle":
            self.starting_size = size
        if orientation is not None:
            self.starting_orientation = orientation
        
class Cell:
    def __init__(self, type_identifier, shape, x, y, height, width):
        self.type_identifier=type_identifier
        self.starting_x = x
        self.starting_y = y
        self.shape = shape
        self.starting_height = height
        self.starting_width=width

    def Draw(self):
        if self.shape == "circle":
            return plt.Circle((self.starting_x,self.starting_y),self.starting_height/2,fill=False)
        elif self.shape == "rectangle":
            return plt.Rectangle([self.starting_x,self.starting_y],self.starting_width,self.starting_height,fill=False)

#define starting cell types
#Adjust so single cell type and multiple starting positions
OverallCellTypes=[]
OverallCellTypes.append(CellTypes("VM",10,"rectangle",0,5,[2,1],'x'))
OverallCellTypes.append(CellTypes("PMEC",10,"rectangle",0,6,[1,2],'x'))
OverallCellTypes.append(CellTypes("PMEC",10,"rectangle",0,12,[1,2],'x'))
OverallCellTypes.append(CellTypes("VM",10,"rectangle",0,14,[2,1],'x'))

Cells=[]


#draw current cells
for type in OverallCellTypes:
    if type.starting_shape=="rectangle":
        x_size = type.starting_size[0]
        y_size = type.starting_size[1]
    elif type.starting_shape=="circle":
        x_size = type.starting_radius
        y_size = type.starting_radius
    for n in range(type.starting_number):

        if type.starting_orientation=='x':
            x_position = type.starting_position[0]+n*x_size
            y_position = type.starting_position[1]
        elif type.starting_orientation == 'y':
            x_position = type.starting_position[0]
            y_position = type.starting_position[1]+n*y_size
        #else:
            ###fill in the gaps of what happens when no orientation - fill the region with n cells

        if type.starting_shape=="rectangle":
            Cells.append(Cell(type_identifier=type.name,
                            shape=type.starting_shape,
                            x=x_position,
                            y=y_position,
                            height=type.starting_size[1],
                            width=type.starting_size[0]))
        elif type.starting_shape=="circle":
            Cells.append(Cell(type_identifier=type.name,
                            shape=type.starting_shape,
                            x=x_position+type.starting_radius/2,
                            y=y_position+type.starting_radius/2,
                            height=type.starting_radius,
                            width=type.starting_radius))

figure, axes = plt.subplots()
axes.set_aspect( 1 )

for cell in Cells:
    axes.add_artist(cell.Draw())

plt.xlim(0, 40)
plt.ylim(0, 20)
plt.title( 'Colored Circle' )
plt.show()







    



