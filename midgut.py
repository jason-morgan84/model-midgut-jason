import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
import Cell
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

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
############1.4: Consider adding to getnodes function to get distance to each of the closest cells (ideally in x/y components)
############1.5: Add collision detection with closest cells only
##########################1.5.1: For testing: Make collision propogate speed through cells
############1.6: Look up potential property to simply define effects of collision - elasticity?
############1.7: Random movement?
#2: Add adhesion
############2.1: Add movement to PMECs
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
TickNumber = 200

#whether to simulate then replay (smoother) or run in realtime (slower and jerkier - for testing)
RealTime = True





#####################################Cell Properties####################################
#Define cell types and starting positions
OverallCellTypes=[]
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
Cells.GetNodeNetwork(1)
#add timer
time = axes.annotate("0s", xy=(20, 20), xytext=(40,17),horizontalalignment='right')


#######################################Simulation#######################################
#Actions to carry out before simulation
#define velocity of cell - present for testing purposes only, wouldn't go here in the end
for cell in Cells:
    #if cell.Type == "PMEC" or cell.Type == "Other": cell.Dynamics.Velocity.X = 0.1
    pass
x=0
while x == 0:
    random_cell=int(np.random.random()*70)
    #print(random_cell)
    #print(Cells[random_cell].Type)
    if Cells[random_cell].Type=='Other':
        Cells[random_cell].Dynamics.Velocity.X = (np.random.random()-0.5)*0.05
        Cells[random_cell].Dynamics.Velocity.Y = (np.random.random()-0.5)*0.05
        break

#Simulation function - defines what to do on each tick of the simulation
#If RealTime is False outputs a list of cell positions, otherwise outputs a list of Artists (shapes) that have changed
def Simulate(i):
    ArtistList=[]
    OutputPositions=[]
    for n,cell in enumerate(Cells):
        #only append cell to artists list if it has forces applied to it or speed that would require redrawing
        if cell.Dynamics.Velocity.AsList() != [0,0] or cell.Dynamics.Force.AsList() != [0,0]:
            #Updates neighbours of moving cell, as well as cells that were neighborus of cell of interest
            #both before and after updating the neighbour list.
            #This may well be slower than updating all nodes with enough movement.
            Update_List=set()
            [Update_List.add(item[0]) for item in cell.Neighbours]
            Cells.UpdateNodeNetwork(n,1)
            [Update_List.add(item[0]) for item in cell.Neighbours]
            [Cells.UpdateNodeNetwork(item,1) for item in Update_List]
            cell.UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
            if RealTime == True: ArtistList.append(cell.artist)
        if RealTime == False:
            OutputPositions.append([cell.Position.Position.X,cell.Position.Position.Y])

    #update timer
    time.set_text(str(i*5)+"s")
    ArtistList.append(time)
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
    ani = animation.FuncAnimation(figure, Simulate, frames=TickNumber, interval=10, blit=True,repeat=False)
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
            if cell.Position.Position.X==center.X and cell.Position.Position.Y==center.Y: 
                #cell.Dynamics.Velocity.X = (np.random.random()-0.5)*0.5
                #cell.Dynamics.Velocity.Y = (np.random.random()-0.5)*0.5
                for item in cell.Neighbours:
                    Cells[item[0]].artist.set_edgecolor('red')     
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