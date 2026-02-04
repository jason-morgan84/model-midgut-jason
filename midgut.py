import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
from matplotlib.backend_bases import MouseButton
import Cell

#Each cell is defined using it's shape (currently, ellipse or rectangle), its center point (using XY class) and 
#its size (using XY class - full width and height, not radius). 
# 
#Characteristics of individual cells are stored in the Cells class and a list of all cells are maintained in the CellList class.
#The CellList class allows adding ("CellList.AddCell(cell)") Cells class objects and iteration through cells.
#
#To draw cells using MatPlotLib, the Cells.Draw function returns a MatPlotLib artist
#To analyse cells using Shapely, the Cells.GetCoords function returns a list of coords to use in a Shapely Polygon
#
#A list of cells neighbouring each cell can be generated using CellList.GetNodeNetwork


#TO DO:

#1: Add movement and collision detection
############1.2: Change cell.Position to include coords of polygon points
############1.3: Add function to update all associated positions with movement
##########################1.3.1 Consider whether all storage positions are required
############1.4: Consider adding to getnodes function to get distance to each of the closest cells (ideally in x/y components)
############1.5: Add collision detection with closest cells only
##########################1.5.1: For testing: Make collision propogate speed through cells
############1.6: Look up potential property to simply define effects of collision - elasticity?
############1.7: Random movement?
#2: Add adhesion
############2.1: Add movement to PMECs
#3: Add legend of cell types
#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm - allow ellipses
############5.2: Finish "Fill" arrangement 
############5.3: Random variation in cell size
############5.3: Custom packing for variably sized rectangles





#define plot and axes
figure, axes = plt.subplots()
axes.set_aspect( 1 )
#axes.set_axis_off()
plt.xlim(0, 40)
plt.ylim(0, 20)
plt.title( 'Drosophila Embryonic Midgut' )

OverallCellTypes=[]

#Define cell types and starting positions
OverallCellTypes.append(Cell.CellTypes(Name = "VM", Format = Cell.Format(FillColour = 'plum'), 
                StartingPosition=
                    [Cell.StartingPosition(
                        ID = "UpperVM",
                        Position = Cell.XY(1,13.5),
                        Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(2,1)),
                        Arrange = "XAlign",
                        Number = 20),
                    Cell.StartingPosition(
                        ID = "LowerVM",
                        Position = Cell.XY(1,3),
                        Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(2,1)),
                        Arrange = "XAlign",
                        Number = 20)]))

OverallCellTypes.append(Cell.CellTypes(Name = "PMEC", Format = Cell.Format(FillColour = 'powderblue'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperPMEC",
                        Position = Cell.XY(0.5,12),
                        Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(1,2)),
                        Arrange = "XAlign",
                        Number = 10),
                    Cell.StartingPosition(
                        ID = "LowerPMEC",
                        Position = Cell.XY(0.5,4.5),
                        Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(1,2)),
                        Arrange = "XAlign",
                        Number = 10)]))

OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(0.75,6.25),
                        Morphology = Cell.Morphology(Shape = 'Ellipse', Size = Cell.XY(1.5,1.5)),
                        Arrange = 'Pack',
                        DrawLimits = Cell.XY(11,11.5),
                        Density = 0.8)]))

#Initialise CellList variable which will contain a list of all cells with positions, shapes, movement etc.
Cells=Cell.CellList()

#for each cell type, intialise starting positions of those cells and add cells to Cells variable
for type in OverallCellTypes:
    for EachCell in type.Initialise():
        Cells.AddCell(EachCell)

for cell in Cells:
    #define velocity of cell - present for testing purposes only, wouldn't go here in the end
    #if cell.Type == "PMEC" or cell.Type == "Other": cell.Dynamics.Velocity.X = 0.1

    #draw cell
    axes.add_artist(cell.Draw())

Nodes=Cells.GetNodeNetwork(1)

# Animation function
def animate(i):
    ArtistList=[]
    #if (i % 20==0): 
    Nodes=Cells.GetNodeNetwork(1)
    for cell in Cells:
        cell.Position.X += cell.Dynamics.Velocity.X
        cell.Position.Y += cell.Dynamics.Velocity.Y
        if cell.Morphology.Shape == 'Rectangle':
            cell.artist.xy = [cell.Position.X-cell.Morphology.Size.X/2,cell.Position.Y-cell.Morphology.Size.Y/2]
        elif cell.Morphology.Shape == 'Ellipse':
            cell.artist.center = cell.Position.AsList()
      
        ArtistList.append(cell.artist)
    return tuple(ArtistList)

ani = animation.FuncAnimation(figure, animate, frames=1000, interval=10, blit=True)



def onpick1(event):

    if isinstance(event.artist, mpatches.Rectangle) or isinstance(event.artist, mpatches.Ellipse):
        for cell in Cells:
            cell.artist.set_edgecolor('black')
        center = Cell.XY(event.artist.get_center()[0],event.artist.get_center()[1])
        for n, cell in enumerate(Cells):
            if cell.Position.X==center.X and cell.Position.Y==center.Y: 
                cell.Dynamics.Velocity.X = (np.random.random()-0.5)*0.5
                cell.Dynamics.Velocity.Y = (np.random.random()-0.5)*0.5
                for item in Nodes[n]:
                    Cells[item].artist.set_edgecolor('red')     
    else:
        print("Reset")
        for cell in Cells:
            cell.artist.set_edgecolor('black')


#plt.connect('button_press_event', on_click)

figure.canvas.mpl_connect('pick_event', onpick1)

plt.show()






    

#re-included if click is needed
""" def on_click(event):
    if event.button is MouseButton.LEFT:
        print(f'data coords {event.xdata} {event.ydata}') """

