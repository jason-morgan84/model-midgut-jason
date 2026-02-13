import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
import Cell
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

#0: Adjust collision
############0.1: As adhesion increases, there's still something odd about collisions - overlap from some angles, bouncing too much from others

#1: Add random movement

#2: Consider changes to adjacency at diagonals
############1.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################1.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent

#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm for circles
##########################5.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
############5.2: Finish "Fill" arrangement 
############5.3: Random variation in cell size

#6: Why do RealTime simulations give different results to Replays and Reports


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
SimulationType = "Replay"

#Variables defining speed of migration
MigrationSpeed = 0.05 #um/Tick
SpeedLimit = 0.06 #um/Tick

AdhesionDistance = 0.1 #ScaleUnits
AdhesionForce = 0.00005 #MassUnits.ScaleUnits.TickLength^-2

MinimumDesiredGap = 0.05
ProximityForce = 0.00005

MigrationForce = 0.0005

EndPointX = 0.5 #defines finish line for measuring in terms of width of simulation
plt.axvline(x = EndPointX * PlotWidth, color = 'lightcoral', alpha = 0.5, linewidth = 2, label = 'Finish Line')

global Finished 
Finished = False

global EndTime 
EndTime = 0

FinishProportion = 0.1
counter = axes.annotate("0/"+str(int(round(NCells*FinishProportion,0))), xy=(20, 21), xytext=(40,1), horizontalalignment='right')
#Simulation function - defines what to do on each tick of the simulation
#If RealTime is False outputs a list of cell positions, otherwise outputs a list of Artists (shapes) that have changed

def Simulate(i):
    global Finished
    global EndTime
    if SimulationType == "RealTime":
        ArtistList=[]
    elif SimulationType == "Replay":
        OutputPositions=[]
    else:
        ArtistList=[]

    Cells.GenerateNodeNetwork(1)

    for n,cell in enumerate(Cells):

        if cell.Type != "VM":
            #Define forces due to speed limits
            Radius = cell.Morphology.Radius

            VelocityX = cell.Dynamics.Velocity.X
            VelocityY = cell.Dynamics.Velocity.Y
            VelocityMagnitude = math.hypot(VelocityY, VelocityX)

            AdhesionForceX = 0
            AdhesionForceY = 0

            SpeedLimitForceX = 0
            SpeedLimitForceY = 0

            if VelocityMagnitude > SpeedLimit:
                SpeedLimitForceMagnitude = VelocityMagnitude - SpeedLimit
                VelocityUnitVectorX = VelocityX/VelocityMagnitude
                VelocityUnitVectorY = VelocityY/VelocityMagnitude
                SpeedLimitForceX = -VelocityUnitVectorX * SpeedLimitForceMagnitude
                SpeedLimitForceY = -VelocityUnitVectorY * SpeedLimitForceMagnitude

            # Define forces related to proximity to other cells
            # These include:
            ####    Repulsion due to overlap
            ####    Attraction due to adhesion
            ####    Signalling from neighbouring cells

            PositionX = cell.Position.X
            PositionY = cell.Position.Y

            ProximityForceX = 0
            ProximityForceY = 0
            ProximityForceMagnitude = 0

            MigrationForceX = 0
            VMAdjacent = False
            for neighbour in cell.Neighbours:
                NeighbourPositionX = Cells[neighbour].Position.X
                NeighbourPositionY = Cells[neighbour].Position.Y
                Distance = math.hypot(NeighbourPositionY - PositionY, NeighbourPositionX - PositionX)
                Gap = Distance - Radius - Cells[neighbour].Morphology.Radius

                # Repulsive forces due to overlap
                # If the distane between the cells is less than the minimum gap, increase repulsive force in opposite direction
                # Once the gap is less than MinimumDesiredGap, the repulsive force increases gradually from 0 in a parabola
                # centred on MinimumDesiredGap, reaching 1 when Gap is 0 and continuing to increase as any overlap increases

                if Gap < MinimumDesiredGap:
          
                    ProximityForceMagnitude = (((1/MinimumDesiredGap) ** 2) * (Gap - 1) ** 2) * ProximityForce
                    DirectionUnitVectorX = (NeighbourPositionX - PositionX) / Distance
                    DirectionUnitVectorY = (NeighbourPositionY - PositionY) / Distance
                    ProximityForceX += -DirectionUnitVectorX * ProximityForceMagnitude
                    ProximityForceY += -DirectionUnitVectorY * ProximityForceMagnitude

                # Attractive forces due to adhesion
                # These are felt as soon as AdhesionDistance * 2 is reached. Attractive forces are at a maximum at 
                # AdhesionDistance * 2, decrease to 0 as Gap approaches AdhesionDistance and are 0 below AdhesionDistance.
                if Gap <= AdhesionDistance * 2:
                    if Gap >= AdhesionDistance:
                        AdhesionForceMagnitude = ((Gap/AdhesionDistance) ** 3) * AdhesionForce
                    elif Gap < AdhesionDistance:
                        AdhesionForceMagnitude = 0


                    DirectionUnitVectorX = (NeighbourPositionX - PositionX) / Distance
                    DirectionUnitVectorY = (NeighbourPositionY - PositionY) / Distance

                    AdhesionForceX += -DirectionUnitVectorX * AdhesionForceMagnitude
                    AdhesionForceY += -DirectionUnitVectorY * AdhesionForceMagnitude
       

                # Forces due to signalling from VM
                # Checks if cell is a PMEC adjacent to (within adhesion distance) of VM. If it is, sets VMAdjacent to true
                # If VMAdjacent is true and cell velocity is lower than migration speed, force in the x direction is increased       
                if cell.Type == "PMEC" and Cells[neighbour].Type == "VM":
                    Distance = math.hypot(NeighbourPositionY - PositionY, NeighbourPositionX - PositionX)
                    VMAdjacent = True

            if VMAdjacent==True and VelocityX < MigrationSpeed:
                MigrationForceX = MigrationForce
        

            TotalForceX = SpeedLimitForceX + ProximityForceX + MigrationForceX + AdhesionForceX
            TotalForceY = SpeedLimitForceY + ProximityForceY + AdhesionForceY

            AccelerationX = TotalForceX/(Radius**2)
            AccelerationY = TotalForceY/(Radius**2)

            VelocityX += AccelerationX * TickLength 
            VelocityY += AccelerationY * TickLength 

            cell.Dynamics.Velocity.X = VelocityX
            cell.Dynamics.Velocity.Y = VelocityY
            
    FinishedCells = 0
    for n, cell in enumerate(Cells):
        
        Cells[n].UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
        if SimulationType == "RealTime": 
            ArtistList.append(cell.artist)
        elif SimulationType == "Replay":
            OutputPositions.append([cell.Position.X,cell.Position.Y])
        else:
            ArtistList.append(cell.artist)


        if cell.Position.X > (PlotWidth * EndPointX) and cell.Type != "VM":
            FinishedCells += 1
    
    #update timer if migration isn't complete
    if FinishedCells >= NCells * FinishProportion and Finished == False:
        Finished = True
        EndTime = i * TickLength
    
    if Finished == False:
        timer.set_text(str(i * TickLength) + "s")
    else:
        timer.set_text(str(EndTime) + "s")
        timer.set_color('r')

    counter.set_text(str(FinishedCells)+"/"+str(int(round(NCells*FinishProportion))))
    

    if SimulationType == "RealTime":
        ArtistList.append(timer)
        ArtistList.append(counter)
        return tuple(ArtistList)
    
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




    

#re-included if click is needed
""" def on_click(event):
    if event.button is MouseButton.LEFT:
        print(f'data coords {event.xdata} {event.ydata}') """

#plt.connect('button_press_event', on_click)