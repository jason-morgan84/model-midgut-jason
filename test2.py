import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
import Cell
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import time

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

#0: Rearrange code to proper files
#1: Add adhesion
############1.1: Create function to relate adhesive power, distance and a linear variable to alter adhesion in an intuitive way
############1.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################1.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent
#2: Add data recording for analysis
#3: Add collision detection
############3.1: Find way to deal with cells that do end up overlapping
############3.2: Find way to deal with cells that are moving at the same speed
#4: Better define edges
#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm - allow ellipses
############5.2: Finish "Fill" arrangement 
############5.3: Random variation in cell size
############5.3: Custom packing for variably sized rectangles
#6: Add randomisation
#7: Consider whether all storage positions are required


#define simulation details
#scale variable defines size of 1 unit in um
scale = 1

#tick length gives length of single tick in seconds
TickLength = 5

#length of simulation in ticks
TickNumber = 1000

#whether to simulate then replay (smoother) or run in realtime (slower and jerkier - for testing)
RealTime = True

#Field properties
#UpperBound=//
#LowerBound=//
#LeftBound=//
#RightBound=//


#####################################Cell Properties####################################
#Define cell types and starting positions
OverallCellTypes=[]

OverallCellTypes.append(Cell.CellTypes(Name = "PMEC", Format = Cell.Format(FillColour = 'powderblue'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperPMEC",
                        Position = Cell.XY(1,13),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 10),
                    Cell.StartingPosition(
                        ID = "LowerPMEC",
                        Position = Cell.XY(1,2),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 10)]))

""" OverallCellTypes.append(Cell.CellTypes(Name = "Leader",Format = Cell.Format(FillColour = 'lightyellow'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(23,4),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = 'YAlign',
                        Number = 4)])) """

OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(1,4),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = 'Pack',
                        DrawLimits = Cell.XY(21,13),
                        Density = 0.8)]))


TopBoundary = 14
LowerBoundary = 1
Edge = mpatches.Rectangle((-1,0.75),50,13.75,fill = False,edgecolor='Plum',linewidth=5)

#####################################Initialisation#####################################
#define plot and axes
figure, axes = plt.subplots()
axes.add_artist(Edge)

#Initialise CellList variable which will contain a list of all cells with positions, shapes, movement etc.
Cells=Cell.CellList()

#for each cell type, intialise starting positions of those cells and add cells to Cells variable
for type in OverallCellTypes:
    for EachCell in type.Initialise():
        Cells.AddCell(EachCell)

#add each cell to axis
for cell in Cells:
    axes.add_artist(cell.Draw())

#get network of neighbouring cells
Cells.GenerateNodeNetwork(1)

#add timer
timer = axes.annotate("0s", xy=(20, 20), xytext=(40,17),horizontalalignment='right')


#######################################Simulation#######################################
#Actions to carry out before simulation

MigrationSpeed = 0.03#um/s
SpeedLimit = 0.06

for cell in Cells:
    if cell.Type == "PMEC":
        cell.Dynamics.Velocity.X = MigrationSpeed



#Simulation function - defines what to do on each tick of the simulation
#If RealTime is False outputs a list of cell positions, otherwise outputs a list of Artists (shapes) that have changed

AdhesionStrength = 0.1
AdhesionChanceToBreak = 0
def AdhesionFunction(distance):
    Adhesion = 1-distance**5
    if Adhesion < 0: Adhesion = 0
    return Adhesion

LeaderCell = 0


#if cell is close, constrain speed
#depending on power of adhesion, speed must be speed of cell +- x



def Simulate(i):
    ArtistList=[]
    OutputPositions=[]
    Cells.GenerateNodeNetwork(1)
    #first loop, work out where each cell wants to go
    for n,cell in enumerate(Cells):
        if cell.Type!="PMEC":
            #if not leader cell
            for neighbour in cell.Neighbours:

                Distance = (math.hypot(cell.Position.X - Cells[neighbour].Position.X,cell.Position.Y - Cells[neighbour].Position.Y) - Cells[neighbour].Morphology.Radius - cell.Morphology.Radius)/Cells[neighbour].Morphology.Radius

                #Function for freedom (ability of cell to move independently)
                # Between 1 and 0
                # A distance of 0 should give a Freedom of of 0
                # As distance increases, Freedom should tend to 1
                # Variable to define ~where Freedom should hit 1 in terms of multiples of cell radius - 1 radius, 2 radiuses etc
                # Variable to define power of adhesion in intuitive way - ie, half the power of adhesion, double the freedom
                
                # Apply function to both speed limit and mean X speed (if Freedom is 1, XSpeed varies around 0, not MigrationSpeed)
                # Need something for stickiness and for distance at which it has an effect



                MinimumRadiusRatio = 0.5 #Increase this to increase the maximum distance at which adhesion can act
                Freedom = (abs(Distance)/MinimumRadiusRatio)**1
                if Freedom < 0: Freedom = 0
                if Freedom > 1: Freedom = 1
           
                Freedom = 1

                #Choose how often to change the speed:
                if np.random.random()<0.1:
                    XSpeed=np.random.normal(MigrationSpeed-MigrationSpeed*Freedom,SpeedLimit*Freedom)
                    cell.Dynamics.Velocity.X = XSpeed
                    YSpeed=np.random.normal(0,SpeedLimit*Freedom)
                    cell.Dynamics.Velocity.Y = YSpeed      
                #print(XSpeed)
            
    #second loop, move each cell
    for n,cell in enumerate(Cells):
        if cell.Type!="Leader":
            Cells.Collision(n)
            cell.UpdatePosition(cell.Dynamics.Velocity.X ,cell.Dynamics.Velocity.Y)

            if RealTime == True: ArtistList.append(cell.artist)
            if RealTime == False:
                OutputPositions.append([cell.Position.Position.X,cell.Position.Position.Y])

    #update timer
    timer.set_text(str(i*5)+"s")
    ArtistList.append(timer)
    return tuple(ArtistList) if RealTime == True else OutputPositions


ani = animation.FuncAnimation(figure, Simulate, frames=TickNumber, interval=40, blit=True,repeat=False)   







####################################Plot properties#####################################
#plot characteristics
axes.set_aspect( 1 )
axes.set_axis_off()
plt.xlim(0, 40)
plt.ylim(0, 20)

#add legend
LegendPatches=[]
for cell in OverallCellTypes:
    LegendPatches.append(mpatches.Patch(color=cell.Format.FillColour, label=cell.Name))
plt.legend(handles=LegendPatches, bbox_to_anchor=(0.19, 1.1))



#axes.add_artist(scalebar)

#add title
#plt.title( 'Drosophila Embryonic Midgut' )

plt.show()

########################################################################################
