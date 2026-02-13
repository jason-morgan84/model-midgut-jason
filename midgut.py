import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
import Cell, CellDynamics
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import time

#Each cell is defined as a circle using its center point (using XY class) and radius (using XY class)
# 
#Characteristics of individual cells are stored in the Cells class and a list of all cells are maintained in the CellList class.
#The CellList class allows adding ("CellList.AddCell(cell)") Cells class objects and iteration through cells.
#
#To draw cells using MatPlotLib, the Cells.Draw function returns a MatPlotLib artist
#
#A list of cells neighbouring each cell can be generated using CellList.GetNodeNetwork


#TO DO:

#2: Consider changes to adjacency at diagonals
############2.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################2.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent

#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm for circles
##########################5.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
############5.2: Finish "Fill" arrangement 
############5.3: Random variation in cell size

#6: Why do RealTime simulations give different results to Replays and Reports

#7: See if its possible to streamline the InitialiseCell function




#####################################Cell Properties####################################
#Define cell types and starting positions
OverallCellTypes=[]

OverallCellTypes.append(Cell.CellTypes(Name = "PMEC", Format = Cell.Format(FillColour = 'powderblue'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperPMEC",
                        Position = Cell.XY(-21,16),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 20),
                    Cell.StartingPosition(
                        ID = "LowerPMEC",
                        Position = Cell.XY(-21,5),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 20)]))

OverallCellTypes.append(Cell.CellTypes(Name = "VM",Format = Cell.Format(FillColour = 'plum'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperVM",
                        Position = Cell.XY(-21,17.5),
                        Morphology = Cell.Morphology(Radius = 0.5),
                        Arrange = "XAlign",
                        Number = 100),
                    Cell.StartingPosition(
                        ID = "LowerVM",
                        Position = Cell.XY(-21,3.5),
                        Morphology = Cell.Morphology(Radius = 0.5),
                        Arrange = "XAlign",
                        Number = 100)]))

OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(-21,7),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = 'Pack',
                        DrawLimits = Cell.XY(21,15.67),
                        Density = 1)]))

""" OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(11,7),
                        Morphology = Cell.Morphology(Radius = 1))])) """

#####################################Initialisation#####################################
#define plot and axes
figure, axes = plt.subplots()

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
timer = axes.annotate("0s", xy=(20, 21), xytext=(40,20),horizontalalignment='right',color = 'black')
NCells = 0
for cell in Cells:
    if cell.Type != "VM":
        NCells += 1


#######################################Simulation#######################################
#Variables defining simulation

PlotWidth = 40 #Width of simulation plot in scale units

#define simulation details
#scale variable defines size of 1 unit in um
Scale = 1

#tick length gives length of single tick in seconds
TickLength = 1

#length of simulation in ticks
TickNumber = 1000

# Whether to run simulation in real time ("RealTime"),
# simulate then replay ("Replay")
# or simulate and report results ("Report")
SimulationType = "RealTime"

#Variables defining speed of migration
MigrationSpeed = 0.05 #um/Tick
SpeedLimit = 0.06 #um/Tick

# AdhesionDistance defines desired separation distance of two stably adhered cells.
# Below AdhesionDistance, no adhesive force is felt.
# AdhesionForceDistance defines the maximum distance at which an attractive force is felt.
# Above AdhesionForceDistance, no attractive force is felt.
# At AdhesionForceDistance, a maximum attractive force is felt.
# This maximum attractive force is defined by AdhesionForce.
# As the gap between the cells decreases from AdhesionForceDistance to AdhesionDistance, attractive force decreases to 0
# According to the formula Force = AdhesionForce * (Gap/AdhesionForceDistance)^3

AdhesionDistance = 0.05 #ScaleUnits
AdhesionForceDistance = AdhesionDistance * 3
AdhesionForce = 0.1 #MassUnits.ScaleUnits.TickLength^-2

MinimumDesiredGap = 0.05
ProximityForce = 0.00005


# Forces for internal forces
# Define maximum force and directionality (tendency of a cell to maintain its desired direction rather than move randomly)
MigrationForce = 0.05
InternalForce = 0.005
Directionality = 0

#Define variables for defining and recording simulation end point
EndPointX = 0.5 #defines finish line for measuring in terms of width of simulation
FinishProportion = 0.1 #proportion of cells to have passed EndPointX for simulation to be considered over
plt.axvline(x = EndPointX * PlotWidth, color = 'lightcoral', alpha = 0.5, linewidth = 2, label = 'Finish Line')
global Finished 
global EndTime 

Finished = False
EndTime = 0

counter = axes.annotate("0/"+str(int(round(NCells*FinishProportion,0))), xy=(20, 21), xytext=(40,1), horizontalalignment='right')


#Simulation function - defines what to do on each tick of the simulation
def Simulate(i):
    global Finished
    global EndTime

    ArtistList=[]

    OutputPositions=[]


    Cells.GenerateNodeNetwork(1)

    for n,cell in enumerate(Cells):

        if cell.Type != "VM":

            #Get cell properties for force calculations
            CellRadius = cell.Morphology.Radius
            CellVelocityX = cell.Dynamics.Velocity.X
            CellVelocityY = cell.Dynamics.Velocity.Y
            CellPosition = cell.Position

            #Set-up force variables
            ProximityForceX, ProximityForceY = 0, 0
            AdhesionForceX, AdhesionForceY = 0, 0
            MigrationForceX = 0

            #loop through each neighbouring cell
            for neighbour in cell.Neighbours:

                #get neighbour cell properties for force calculations
                NeighbourPosition = Cells[neighbour].Position
                NeighbourRadius = Cells[neighbour].Morphology.Radius

                #get forces due to proximity from each neighbour and increment
                NewProximityForceX, NewProximityForceY = CellDynamics.Proximity(MinimumDesiredGap,ProximityForce,CellPosition, NeighbourPosition, CellRadius, NeighbourRadius)
                ProximityForceX += NewProximityForceX
                ProximityForceY += NewProximityForceY
                
                #get forces due to adhesions from each neighbour and increment
                NewAdhesionForceX, NewAdhesionForceY = CellDynamics.Adhesion(AdhesionDistance,AdhesionForceDistance,AdhesionForce, CellPosition, NeighbourPosition, CellRadius, NeighbourRadius)
                AdhesionForceX += NewAdhesionForceX
                AdhesionForceY += NewAdhesionForceY

                #get list of neighbouring cell types to define forces due to signalling from neighbours
                AdjacentCellType = CellDynamics.Signalling(cell.Type, Cells[neighbour].Type, CellPosition, NeighbourPosition)

            #get drag forces due to excessive speed
            SpeedLimitForceX, SpeedLimitForceY = CellDynamics.Drag(CellVelocityX, CellVelocityY, SpeedLimit)

            #get forces from cell intrinsic activities
            InternalForceX, InternalForceY = CellDynamics.IntrinsicForces(cell.Dynamics.InternalForce, InternalForce, Directionality)
            
            #update forces due to neighbouring cell types
            for item in AdjacentCellType or []:
                if item == "VM":
                    if VelocityX < MigrationSpeed:
                        MigrationForceX = MigrationForce   

            #sum x and y force components
            TotalForceX = SpeedLimitForceX + ProximityForceX + MigrationForceX + AdhesionForceX + InternalForceX
            TotalForceY = SpeedLimitForceY + ProximityForceY + AdhesionForceY + InternalForceY

            #calcuate acceleration components proportional to radius squared (assumes equal cell densities)
            AccelerationX = TotalForceX/(CellRadius**2)
            AccelerationY = TotalForceY/(CellRadius**2)

            #increments cell velocity components based on acceleration and TickLength (in us)
            VelocityX += AccelerationX * TickLength 
            VelocityY += AccelerationY * TickLength 

            #sets new values of velocity components for each cell
            cell.Dynamics.Velocity.X = VelocityX
            cell.Dynamics.Velocity.Y = VelocityY

            #sets new cell internal forces
            cell.Dynamics.InternalForce.X = InternalForceX
            cell.Dynamics.InternalForce.Y = InternalForceY
            
    FinishedCells = 0
    #for each cell, updates position due to calculated velocity and appends cell artist information or positions as required
    #due to simulation types.
    #this is a separate loop in order to update all cell velocities before starting to change positions
    for n, cell in enumerate(Cells):
        Cells[n].UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
        if SimulationType == "RealTime": 
            ArtistList.append(cell.artist)
        elif SimulationType == "Replay":
            OutputPositions.append([cell.Position.X,cell.Position.Y])
        else:
            pass

        #count number of cells that have passed the finish line
        if cell.Position.X > (PlotWidth * EndPointX) and cell.Type != "VM":
            FinishedCells += 1
    
    #if finishing requirements are met, set simulation as finished and save end time
    if FinishedCells >= NCells * FinishProportion and Finished == False:
        Finished = True
        EndTime = i * TickLength
    
    #update timer - if not finished, increment by ticklength, if finished, set to end time
    if Finished == False:
        timer.set_text(str(i * TickLength) + "s")
    else:
        timer.set_text(str(EndTime) + "s")
        timer.set_color('r')

    #update counter for cells that have reached finish requirements
    counter.set_text(str(FinishedCells)+"/"+str(int(round(NCells*FinishProportion))))
    
    #return artist list for real time simulation
    if SimulationType == "RealTime":
        ArtistList.append(timer)
        ArtistList.append(counter)
        return tuple(ArtistList)
    
    #return positions for replayed simulation
    elif SimulationType == "Replay":
        return OutputPositions


#########################################Replay#########################################
#Replay function - if not being run in real time, goes through each saved position and moves cells accordingly
def Replay(i):
    ArtistList=[]
    for n, CellPosition in enumerate(RecordedPositions[i]):
        Cells[n].SetPosition(CellPosition[0],CellPosition[1])
        ArtistList.append(Cells[n].artist)
    timer.set_text(str(i*TickLength)+"s")
    ArtistList.append(timer)
    return tuple(ArtistList)

#If running in real time, runs simulation and updates output plots
#If not running in real time, runs the simulation through and saves position of each cell at each tick, the draws animation based
#on this saved data
if SimulationType == "RealTime":
    ani = animation.FuncAnimation(figure, func = Simulate, frames=TickNumber, interval=40, blit=True,repeat=False)

elif SimulationType == "Replay":
    RecordedPositions=[]
    for tick in range(TickNumber):
        if Finished == False:
            NewPosition = Simulate(tick)
            RecordedPositions.append(NewPosition)
        else:
            break
    ani = animation.FuncAnimation(figure, Replay, frames=len(RecordedPositions), interval=10, blit=True, repeat=False)

elif SimulationType == "Report":
    for tick in range(TickNumber):
        if Finished == False:
            Simulate(tick)
        else:
            print(str(FinishProportion*100)+"% of cells covered "+str(EndPointX * PlotWidth)+"uM in " + str(EndTime) + "s")
            break

    
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
if SimulationType == "Real Time": figure.canvas.mpl_connect('pick_event', onpick1)



####################################Plot properties#####################################
#plot characteristics
axes.set_aspect( 1 )
axes.set_axis_off()
plt.xlim(0, PlotWidth)
plt.ylim(0, 25)

#add legend
LegendPatches=[]
for cell in OverallCellTypes:
    LegendPatches.append(mpatches.Patch(color=cell.Format.FillColour, label=cell.Name))
plt.legend(handles=LegendPatches, bbox_to_anchor=(0.19, 1.1))

#add scalebar
scalebar = AnchoredSizeBar(axes.transData,
                           10*Scale, str(Scale*10) +'um', loc = 'lower right', 
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

