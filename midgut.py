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

#0: Fix neighbours, check everythings working with circles
#1: Add collision detection
############1.2: Add collision detection with closest cells only
##########################1.5.1: For testing: Make collision propogate speed through cells
############1.6: Look up potential property to simply define effects of collision - elasticity?
############1.7: Random movement?
#2: Add adhesion
############2.1: Add movement to PMECs
############2.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################2.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent
#3: Better define edges
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

OverallCellTypes.append(Cell.CellTypes(Name = "Cell", Format = Cell.Format(FillColour = 'powderblue'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Mover",
                        Position = Cell.XY(7,6.5),
                        Morphology = Cell.Morphology(Radius = 1)),
                    Cell.StartingPosition(
                        ID = "Mover2",
                        Position = Cell.XY(9,10),
                        Morphology = Cell.Morphology(Radius = 1)),
                    Cell.StartingPosition(
                        ID = "Mover3",
                        Position = Cell.XY(12.5,10),
                        Morphology = Cell.Morphology(Radius = 1)),
                    #Cell.StartingPosition(
                    #    ID = "Mover4",
                    #    Position = Cell.XY(8,2),
                    #    Morphology = Cell.Morphology(Radius = 1)),
                    Cell.StartingPosition(
                        ID = "Stander",
                        #Position = Cell.XY(10,5),
                        Position = Cell.XY(10,5),
                        Morphology = Cell.Morphology(Radius = 2))]))


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


#Cells[0].Dynamics.Velocity.Y=-0.02    
Cells[0].Dynamics.Velocity.X=0.001
#Cells[1].Dynamics.Velocity.Y=-0.05
#Cells[1].Dynamics.Force.X=0.05  
#Cells[2].Dynamics.Velocity.Y=-0.05   
#Cells[2].Dynamics.Velocity.X=-0.05  
Cells[3].Dynamics.Velocity.X=-0.001   
#Cells[3].Dynamics.Velocity.X=0.05  

#Simulation function - defines what to do on each tick of the simulation
#If RealTime is False outputs a list of cell positions, otherwise outputs a list of Artists (shapes) that have changed

def Simulate(i):
    ArtistList=[]
    OutputPositions=[]
    Cells.GenerateNodeNetwork(1)
    for n,cell in enumerate(Cells):
        #print(n,cell.Neighbours)
        #only append cell to artists list if it has forces applied to it or speed that would require redrawing
        if cell.Dynamics.Velocity.AsList() != [0,0] or cell.Dynamics.Force.AsList() != [0,0]:
                #Update velocities from speed - force gives a maximum speed (resistance to further acceleration is assumed at this point)
                #Assuming consistent densities of cell, mass in 2D is proportional to radius squared


                Cells.Collision(n)
                VelocityX = cell.Dynamics.Velocity.X 
                VelocityY = cell.Dynamics.Velocity.Y

                #AccelerationX = cell.Dynamics.Force.X/cell.Morphology.Radius**2
                #AccelerationY = cell.Dynamics.Force.Y/cell.Morphology.Radius**2
                #VelocityX += AccelerationX
                #if (abs(VelocityX) > abs(cell.Dynamics.Force.X)) and abs(cell.Dynamics.Force.X != 0) :
                #    VelocityX = cell.Dynamics.Force.X

                #VelocityY += AccelerationY

                i#f (abs(VelocityY) > abs(cell.Dynamics.Force.Y)) and abs(cell.Dynamics.Force.Y != 0) :
                 #   VelocityY = cell.Dynamics.Force.Y

                cell.UpdatePosition(VelocityX,VelocityY)
                #cell.Dynamics.Velocity.X = VelocityX
                #cell.Dynamics.Velocity.Y = VelocityY

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