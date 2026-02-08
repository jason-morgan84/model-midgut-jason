import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
import Cell
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import time
import statistics
import copy
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
                        Position = Cell.XY(1,15),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 10),
                    Cell.StartingPosition(
                        ID = "LowerPMEC",
                        Position = Cell.XY(1,5),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 10)]))

OverallCellTypes.append(Cell.CellTypes(Name = "VM",Format = Cell.Format(FillColour = 'plum'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperVM",
                        Position = Cell.XY(-1,17),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 25),
                    Cell.StartingPosition(
                        ID = "LowerVM",
                        Position = Cell.XY(-1,3),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 25)]))

OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(1,7),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = 'Pack',
                        DrawLimits = Cell.XY(21,14),
                        Density = 0.9)]))


TopBoundary = 14
LowerBoundary = 1
#Edge = mpatches.Rectangle((-1,0.75),50,13.75,fill = False,edgecolor='Plum',linewidth=5)

#####################################Initialisation#####################################
#define plot and axes
figure, axes = plt.subplots()
#axes.add_artist(Edge)

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
NCells = 0
for cell in Cells:
    NCells += 1


#######################################Simulation#######################################
#Actions to carry out before simulation

MigrationSpeed = 0.05#um/s
SpeedLimit = 0.06

#Simulation function - defines what to do on each tick of the simulation
#If RealTime is False outputs a list of cell positions, otherwise outputs a list of Artists (shapes) that have changed



#if cell is close, constrain speed
#depending on power of adhesion, speed must be speed of cell +- x



def Simulate(i):
    ArtistList=[]
    OutputPositions=[]
    Cells.GenerateNodeNetwork(1)
    #first loop, work out where each cell wants to go
    for n,cell in enumerate(Cells):
        AdhesionDistance = 0.2
        MigrationForce = 0.00001
        if cell.Type != "VM":
            MaxMigrationForceX = 0
            #Define forces due to speed limits
            VelocityX = cell.Dynamics.Velocity.X
            VelocityY = cell.Dynamics.Velocity.Y
            VelocityMagnitude = math.hypot(VelocityY, VelocityX)

            SpeedLimitForceX = 0
            SpeedLimitForceY = 0

            if VelocityMagnitude > SpeedLimit:
                SpeedLimitForceMagnitude = VelocityMagnitude - SpeedLimit
                VelocityUnitVectorX = VelocityX/VelocityMagnitude
                VelocityUnitVectorY = VelocityY/VelocityMagnitude
                SpeedLimitForceX = -VelocityUnitVectorX * SpeedLimitForceMagnitude
                SpeedLimitForceY = -VelocityUnitVectorY * SpeedLimitForceMagnitude

            #Define forces due to proximity
            MinimumDesiredGap = 0
            PositionX = cell.Position.X
            PositionY = cell.Position.Y
            ProximityForceX = 0
            ProximityForceY = 0
            ProximityForceMagnitude = 0
            for neighbour in cell.Neighbours:
                NeighbourPositionX = Cells[neighbour].Position.X
                NeighbourPositionY = Cells[neighbour].Position.Y
                Distance = math.hypot(NeighbourPositionY - PositionY, NeighbourPositionX - PositionX)
                Gap = Distance - cell.Morphology.Radius - Cells[neighbour].Morphology.Radius + 0.001
                if Gap < MinimumDesiredGap:
                    ProximityForceMagnitude = 0#abs((1/Distance))/100000
                    DirectionUnitVectorX = (NeighbourPositionX - PositionX) / Distance
                    DirectionUnitVectorY = (NeighbourPositionY - PositionY) / Distance
                    ProximityForceX += -DirectionUnitVectorX * ProximityForceMagnitude
                    ProximityForceY += -DirectionUnitVectorY * ProximityForceMagnitude
            

            VMAdjacent = False
            #Forces due to signalling from VM
            if cell.Type == "PMEC":
                MaxMigrationForceX = 0
                
                for neighbour in cell.Neighbours:
                    if Cells[neighbour].Type == "VM":
                        VMAdjacent = True
                        """VerticalDistance = cell.Position.X - Cells[neighbour].Position.X
                        if (VerticalDistance) < AdhesionDistance:
                            MigrationForceX = MigrationForce
                        elif VerticalDistance < 2 * AdhesionDistance:
                            MigrationForceX = 1 - (1/AdhesionDistance) * (VerticalDistance - AdhesionDistance)
                        else:
                            MigrationForceX = 0
                        if MigrationForceX > MaxMigrationForceX: MaxMigrationForceX = MigrationForceX """


            TotalForceX = SpeedLimitForceX + ProximityForceX + MaxMigrationForceX
            TotalForceY = SpeedLimitForceY + ProximityForceY
            if VMAdjacent == True and VelocityX<MigrationSpeed: TotalForceX+=0.01

            AccelerationX = TotalForceX/(cell.Morphology.Radius**2)
            AccelerationY = TotalForceY/(cell.Morphology.Radius**2)

            VelocityX += AccelerationX * TickLength 
            VelocityY += AccelerationY * TickLength 

            cell.Dynamics.Velocity.X = VelocityX
            cell.Dynamics.Velocity.Y = VelocityY

        

    for n, cell in enumerate(Cells):
        
        Cells[n].UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
        if RealTime == True: ArtistList.append(cell.artist)
        if RealTime == False:
            OutputPositions.append([cell.Position.Position.X,cell.Position.Position.Y])

    #update timer
    timer.set_text(str(i*5)+"s")
    ArtistList.append(timer)
    return tuple(ArtistList) if RealTime == True else OutputPositions


#########################################Replay#########################################
#Replay function - if not being run in real time, goes through each saved position and moves cells accordingly
def Replay(i):
    ArtistList=[]
    for n, CellPosition in enumerate(RecordedPositions[i]):
        Cells[n].SetPosition(CellPosition[0],CellPosition[1])
        ArtistList.append(Cells[n].artist)
    time.set_text(str(i*5)+"s")
    ArtistList.append(time)
    return tuple(ArtistList)

#If running in real time, runs simulation and updates output plots
#If not running in real time, runs the simulation through and saves position of each cell at each tick, the draws animation based
#on this saved data
if RealTime == True:
    ani = animation.FuncAnimation(figure, Simulate, frames=TickNumber, interval=40, blit=True,repeat=False)
    pass
elif RealTime == False:
    RecordedPositions=[]
    for tick in range(TickNumber):
        NewPosition = Simulate(tick)
        RecordedPositions.append(NewPosition)
    ani = animation.FuncAnimation(figure, Replay, frames=TickNumber, interval=10, blit=True, repeat=False)
    




######################################Interaction#######################################
#what to do on mouse click - only works when running in real time
def onpick1(event):
    if isinstance(event.artist, mpatches.Rectangle) or isinstance(event.artist, mpatches.Ellipse):
        for cell in Cells:
            cell.artist.set_edgecolor('black')
        center = Cell.XY(event.artist.get_center()[0],event.artist.get_center()[1])
        for n, cell in enumerate(Cells):
            if cell.Position.X==center.X and cell.Position.Y==center.Y: 
                #cell.Dynamics.Velocity.X = (np.random.random()-0.5)*0.5
                #cell.Dynamics.Velocity.Y = (np.random.random()-0.5)*0.5
                #print(cell.Neighbours)
                for item in cell.Neighbours:
                    Cells[item].artist.set_edgecolor('red')     
    else:
        for cell in Cells:
            cell.artist.set_edgecolor('black')
if RealTime == True: figure.canvas.mpl_connect('pick_event', onpick1)



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

#add scalebar
scalebar = AnchoredSizeBar(axes.transData,
                           10*scale, str(scale*10) +'um', loc = 'lower right', 
                           color='grey',
                           frameon=False,
                           size_vertical=1,
                           bbox_transform=figure.transFigure,
                           bbox_to_anchor=(0.9, 0.2))

#axes.add_artist(scalebar)

#add title
#plt.title( 'Drosophila Embryonic Midgut' )

plt.show()

########################################################################################




    

#re-included if click is needed
""" def on_click(event):
    if event.button is MouseButton.LEFT:
        print(f'data coords {event.xdata} {event.ydata}') """

#plt.connect('button_press_event', on_click)