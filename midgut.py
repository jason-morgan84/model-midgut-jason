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
############1.1: Random movement
#2: Consider whether it would be better to store coords of all polygons and increment with movement, or re-calcluate coords whenver
#needed - depends how often coords are generated.
#3: Add legend of cell types
#4: Move cell initialisation into a relevant class
############4.1: Create new class for lists of cell types
############4.2: Move cell initialisation into this class
############4.3: reorder definitions - cell types first (with empty arrays for starting locations) then starting locations
#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm - allow ellipses
############5.2: Finish "Fill" arrangement 
############5.3: Random variation in cell size
############5.3: Custome packing for variably sized rectangles





#define plot and axes
figure, axes = plt.subplots()
axes.set_aspect( 1 )
#axes.set_axis_off()
plt.xlim(0, 40)
plt.ylim(0, 20)
plt.title( 'Drosophila Embryonic Midgut' )


#define starting positions
VMStartingPositions=[]
VMStartingPositions.append(Cell.StartingPosition(
    ID = "UpperVM",
    Position = Cell.XY(1,13.5),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(2,1)),
    Arrange = "XAlign",
    Number = 20))
VMStartingPositions.append(Cell.StartingPosition(
    ID = "LowerVM",
    Position = Cell.XY(1,3),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(2,1)),
    Arrange = "XAlign",
    Number = 20))

PMECStartingPositions=[]
PMECStartingPositions.append(Cell.StartingPosition(
    ID = "UpperPMEC",
    Position = Cell.XY(0.5,12),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(1,2)),
    Arrange = "XAlign",
    Number = 10))
PMECStartingPositions.append(Cell.StartingPosition(
    ID = "LowerPMEC",
    Position = Cell.XY(0.5,4.5),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(1,2)),
    Arrange = "XAlign",
    Number = 10))

OtherStartingPositions=[]
OtherStartingPositions.append(Cell.StartingPosition(
    ID = "Other",
    Position = Cell.XY(0.75,6.25),
    Morphology = Cell.Morphology(Shape = 'Ellipse', Size = Cell.XY(1.5,1.5)),
    Arrange = 'Pack',
    DrawLimits = Cell.XY(11,11.5),
    Density = 0.8))

#define starting cell types
OverallCellTypes=[]
OverallCellTypes.append(Cell.CellTypes(Name = "VM", StartingPosition = VMStartingPositions, Format = Cell.Format(FillColour = 'plum')))
OverallCellTypes.append(Cell.CellTypes(Name = "PMEC", StartingPosition = PMECStartingPositions, Format = Cell.Format(FillColour = 'powderblue')))
OverallCellTypes.append(Cell.CellTypes(Name = "Other", StartingPosition = OtherStartingPositions, Format = Cell.Format(FillColour = 'palegreen')))

Cells=Cell.CellList()
#initialise cells
for type in OverallCellTypes:
    print(type)
    for position in type.StartingPosition:
            print(position)
            if position.Arrange == 'Pack':
                if position.Density != 0:
                    #current method only works for circles as test - add in advanced layer algorithm for ellipse packing
                    #Dmitrii N. Ilin & Marc Bernacki, 2016, Advancing layer algorithm of dense ellipse packing for generating statistically equivalent polygonal structures
                    MaxCellsRow = int((abs(position.DrawLimits.X - position.Position.X)) / (position.Morphology.Size.X/position.Density))
                    VertDistance = (math.sin(math.pi / 3) * position.Morphology.Size.Y) / position.Density
                    MaxRows = int((abs(position.DrawLimits.Y - position.Position.Y)) / VertDistance)
                    n = 0
                    for y in range(MaxRows):
                        y_position = position.Position.Y + y * VertDistance
                        for x in range(MaxCellsRow):
                            n = n + 1
                            if (y % 2 == 0):
                                x_position = position.Position.X + x * (position.Morphology.Size.X/position.Density)
                            else:
                                x_position = position.Position.X + x * (position.Morphology.Size.X/position.Density) + position.Morphology.Size.X / 2
                            Cells.AddCell(Cell.Cells(
                                ID = '-'.join((type.Name, position.ID, str(n))),
                                Type = type.Name,
                                Position = Cell.XY(x_position, y_position),
                                Morphology = position.Morphology,
                                Format = type.Format,
                                Dynamics = Cell.Dynamics(Velocity = Cell.XY(0,0), Force = Cell.XY(0,0))))
            elif position.Arrange == 'XAlign' or position.Arrange == 'YAlign':
                print("Hello")
                for n in range(position.Number):
                    if position.Arrange == 'XAlign':
                        x_position = position.Position.X + position.Morphology.Size.X * n
                        y_position = position.Position.Y
                    elif position.Arrange == 'YAlign':
                        x_position = position.Position.X
                        y_position = position.Position.Y + position.Morphology.Size.Y * n                        
                    Cells.AddCell(Cell.Cells(
                        ID = '-'.join((type.Name,position.ID,str(n))),
                        Type = type.Name,
                        Position = Cell.XY(float(x_position), float(y_position)),
                        Morphology = position.Morphology,
                        Format = type.Format,
                        Dynamics = Cell.Dynamics(Velocity = Cell.XY(0,0), Force = Cell.XY(0,0))))
            else:
                x_position = position.Position.X
                y_position = position.Position.Y
                Cells.AddCell(Cell.Cells(
                    ID = '-'.join((type.Name,position.ID)),
                    Type = type.Name,
                    Position = Cell.XY(float(x_position), float(y_position)),
                    Morphology = position.Morphology,
                    Format = type.Format,
                    Dynamics = Cell.Dynamics(Velocity = Cell.XY(0,0), Force = Cell.XY(0,0))))


for cell in Cells:
    #define velocity of cell
    #if cell.Type == "PMEC" or cell.Type == "Other": cell.Dynamics.Velocity.X = 0.1

    #draw cell
    axes.add_artist(cell.Draw())

Nodes=Cells.GetNodeNetwork(1)

# Animation function
def animate(i):
    ArtistList=[]
    for cell in Cells:
        cell.Position.X += cell.Dynamics.Velocity.X
        cell.Position.Y += cell.Dynamics.Velocity.Y
        cell.artist.zorder = 0
        if cell.Morphology.Shape == 'Rectangle':
            cell.artist.xy = [cell.Position.X-cell.Morphology.Size.X/2,cell.Position.Y-cell.Morphology.Size.Y/2]
        elif cell.Morphology.Shape == 'Ellipse':
            cell.artist.center = cell.Position.AsList()
      
        ArtistList.append(cell.artist)
    
    return tuple(ArtistList)

ani = animation.FuncAnimation(figure, animate, frames=1000, interval=1, blit=True)


""" def on_click(event):
    if event.button is MouseButton.LEFT:
        print(f'data coords {event.xdata} {event.ydata}') """

def onpick1(event):
    if isinstance(event.artist, mpatches.Rectangle) or isinstance(event.artist, mpatches.Ellipse):
        for cell in Cells:
            cell.artist.set_edgecolor('black')
        center = Cell.XY(event.artist.get_center()[0],event.artist.get_center()[1])
        for n, cell in enumerate(Cells):
            if cell.Position.X==center.X and cell.Position.Y==center.Y: 
                Neighbours = Cells.Neighbours(n,1.5)
                #print(n, Neighbours,Nodes[n])
                for item in Nodes[n]:
                    Cells[item].artist.set_edgecolor('red')     
    else:
        print("Reset")
        for cell in Cells:
            cell.artist.set_edgecolor('black')


#plt.connect('button_press_event', on_click)

figure.canvas.mpl_connect('pick_event', onpick1)

plt.show()






    



