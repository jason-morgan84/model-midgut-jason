##########################Midgut.py
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

#1: Add collision detection
############1.5: Add collision detection with closest cells only
##########################1.5.1: For testing: Make collision propogate speed through cells
############1.6: Look up potential property to simply define effects of collision - elasticity?
############1.7: Random movement?
#2: Add adhesion
############2.1: Add movement to PMECs
#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm for circles
##########################5.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
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
TickNumber = 500

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
                        Density = 0.85)]))

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
    if Cells[random_cell].Type=='Other':
        Cells[random_cell].Dynamics.Velocity.X = (np.random.random()-0.5)*0.05
        Cells[random_cell].Dynamics.Velocity.Y = (np.random.random()-0.5)*0.05
        break

#Simulation function - defines what to do on each tick of the simulation
#If RealTime is False outputs a list of cell positions, otherwise outputs a list of Artists (shapes) that have changed
def Simulate(i):
    ArtistList=[]
    OutputPositions=[]
    #Cells.UpdateNodeNetwork(1)
    for n,cell in enumerate(Cells):
        #only append cell to artists list if it has forces applied to it or speed that would require redrawing
        if cell.Dynamics.Velocity.AsList() != [0,0] or cell.Dynamics.Force.AsList() != [0,0]:
            Cells.Collision(n)
            #print(cell.Neighbours)
            #Updates neighbours of moving cell, as well as cells that were neighborus of cell of interest
            #both before and after updating the neighbour list.
            #This may well be slower than updating all nodes with enough movement.
            #Update_List=set()
            #[Update_List.add(item[0]) for item in cell.Neighbours]
            #Cells.UpdateNeighbours(n,1)
            #[Update_List.add(item[0]) for item in cell.Neighbours]
            #[Cells.UpdateNeighbours(item,1) for item in Update_List]
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
    ani = animation.FuncAnimation(figure, Simulate, frames=TickNumber, interval=100, blit=True,repeat=False)
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


##########################Cell.py

import matplotlib.patches as mpatches
import shapely.geometry as sg
import math
import shapely
import time

class XY:
    def __init__(self, X=0, Y=0):
        self.X=X
        self.Y=Y

  
    def AsList(self):
        ClassToList = [self.X,self.Y]
        return ClassToList
    
    def AsTuple(self):
        ClassToTuple = (self.X,self.Y)
        return ClassToTuple
    
    def __str__(self):
        return '[' + str(self.X)+', '+str(self.Y)+']'

class CellTypes:
    def __init__(self, Name, StartingPosition, Format):
        self.Name=Name
        self.StartingPosition = StartingPosition
        self.Format=Format

    def Initialise(self):
        OutputCellList=[]
        for position in self.StartingPosition:
            if position.Arrange == 'Pack':
                if position.Density != 0:
                    #current method only works for circles as test - add in advanced layer algorithm for ellipse packing
                    #Dmitrii N. Ilin & Marc Bernacki, 2016, Advancing layer algorithm of dense ellipse packing for generating statistically equivalent polygonal structures
                    WdithToFill = (abs(position.DrawLimits.X - position.Position.X))
                    HeightToFill = (abs(position.DrawLimits.Y - position.Position.Y))
                    MaxCellsRow = int(WdithToFill / (position.Morphology.Size.X/position.Density))
                    VertDistance = (math.sin(math.pi / 3) * position.Morphology.Size.Y) / position.Density
                    MaxRows = int(HeightToFill / VertDistance)
                    n = 0
                    for y in range(MaxRows):
                        y_position = position.Position.Y + y * VertDistance + (HeightToFill-MaxRows*VertDistance)/2
                        for x in range(MaxCellsRow):
                            n = n + 1
                            if (y % 2 == 0):
                                x_position = position.Position.X + x * (position.Morphology.Size.X/position.Density)
                            else:
                                x_position = position.Position.X + x * (position.Morphology.Size.X/position.Density) + position.Morphology.Size.X / 2
                            NewCell = Cells(
                                ID = '-'.join((self.Name, position.ID, str(n))),
                                Type = self.Name,
                                Position = Position(XY(x_position, y_position),[]),
                                Morphology = position.Morphology,
                                Format = self.Format,
                                Dynamics = Dynamics(Velocity = XY(0,0), Force = XY(0,0)),
                                Neighbours=[])
                            NewCell.Position.Vertices = NewCell.GetCellCoords()       
                            OutputCellList.append(NewCell)
            elif position.Arrange == 'XAlign' or position.Arrange == 'YAlign':
                for n in range(position.Number):
                    if position.Arrange == 'XAlign':
                        x_position = position.Position.X + position.Morphology.Size.X * n
                        y_position = position.Position.Y
                    elif position.Arrange == 'YAlign':
                        x_position = position.Position.X
                        y_position = position.Position.Y + position.Morphology.Size.Y * n                        

                    NewCell=Cells(
                        ID = '-'.join((self.Name,position.ID,str(n))),
                        Type = self.Name,
                        Position = Position(XY(x_position, y_position),[]),
                        Morphology = position.Morphology,
                        Format = self.Format,
                        Dynamics = Dynamics(Velocity = XY(0,0), Force = XY(0,0)),
                        Neighbours=[])
                    NewCell.Position.Vertices = NewCell.GetCellCoords()                   
                    OutputCellList.append(NewCell)
            else:
                x_position = position.Position.X
                y_position = position.Position.Y
                NewCell = Cells(
                    ID = '-'.join((self.Name,position.ID)),
                    Type = self.Name,
                    Position = Position(XY(x_position, y_position),[]),
                    Morphology = position.Morphology,
                    Format = self.Format,
                    Dynamics = Dynamics(Velocity = XY(0,0), Force = XY(0,0)),
                    Neighbours=[])
                NewCell.Position.Vertices = NewCell.GetCellCoords()
                OutputCellList.append(NewCell)
        return OutputCellList

class StartingPosition:
    #removed for kwargs
    def __init__(self, ID, Position, Morphology, **kwargs):
        self.ID = ID #pass identified of starting location
        self.Morphology = Morphology #class containing information about cells shape and size
        self.Position = Position #position of center of first cell as list [x,y]

        #optional definitions of arrangement of cells.
        # XAlign aligns Number cells in a row (ellipse or rectangle) 
        # YAlign aligns Number cells in a column (ellipse or rectangle) 
        # Fill fills a rectangular region defined from Position to Drawlimits (ellipse or rectangle) **not currently created
        # Pack fits cells into a rectangular region defined from Position to Drawlimits (circle only) at a given Density (1 = maximum density, 0 = no cells)
        self.Arrange = kwargs.get('Arrange',None)
        self.Number = kwargs.get('Number',None)
        self.DrawLimits = kwargs.get('DrawLimits',None)
        self.Density = kwargs.get('Density',None)

class Position:
    def __init__(self, Position, Vertices, Orientation = 0):
        self.Position = Position
        self.Vertices = Vertices
        self.Orientation = Orientation

class Morphology:
    def __init__(self, Shape, Size):
        self.Shape = Shape
        self.Size = Size
        
class Format:
    def __init__(self, FillColour='White', LineColour='Black', LineWidth=1):
        self.FillColour=FillColour
        self.LineColour = LineColour
        self.LineWidth = LineWidth

class Dynamics:
    def __init__(self, Velocity=[0,0], Force = [0,0]):
        self.Velocity=Velocity
        self.Force = Force

class Cells:
    def __init__(self, ID, Type, Position, Morphology, Format, Dynamics, Neighbours):
        self.ID=ID
        self.Type=Type #Type of cell should match an item in CellTypes
        self.Position = Position #Class containing information about cells position, orientation. Also stores coords of vertices.
        self.Morphology = Morphology #class containing information about cells shape and size
        self.Format = Format #class containing information about the cells fill and line colour
        self.Dynamics = Dynamics #class containing information about cell speed and forces applied
        self.Neighbours = Neighbours #list of XY coordinates of nearby cells 

    def __getitem__(self,index):
        return getattr(self,index)
   
    def Draw(self):
        if self.Morphology.Shape == "Ellipse":
            self.artist = mpatches.Ellipse(
                xy = tuple(self.Position.Position.AsList()),
                width = self.Morphology.Size.X,
                height = self.Morphology.Size.Y,
                fill = True,edgecolor=self.Format.LineColour,
                facecolor = self.Format.FillColour,
                picker = True,
                zorder = 5)
            return self.artist
        
        elif self.Morphology.Shape == "Rectangle":
            self.artist = mpatches.Rectangle(
                xy = tuple([float(self.Position.Position.X - self.Morphology.Size.X/2), self.Position.Position.Y - self.Morphology.Size.Y / 2]),
                width = self.Morphology.Size.X,
                height = self.Morphology.Size.Y,
                fill = True,
                edgecolor = self.Format.LineColour,
                facecolor = self.Format.FillColour,
                picker = True,
                zorder = 5)
            return self.artist
        
    def UpdatePosition(self,XChange,YChange):
        self.Position.Position.X += XChange
        for coord in self.Position.Vertices:
            coord[0] += XChange
            coord[1] += YChange
        self.Position.Position.Y += YChange
        if self.Morphology.Shape == 'Rectangle':
            self.artist.xy = [self.Position.Position.X-self.Morphology.Size.X/2,self.Position.Position.Y-self.Morphology.Size.Y/2]
        elif self.Morphology.Shape == 'Ellipse':
            self.artist.center = self.Position.Position.AsList()


    def SetPosition(self,X,Y):
        self.Position.Position.X = X
        self.Position.Position.Y = Y
        self.Position.Vertices = self.GetCellCoords()
        if self.Morphology.Shape == 'Rectangle':
            self.artist.xy = [self.Position.Position.X-self.Morphology.Size.X/2,self.Position.Position.Y-self.Morphology.Size.Y/2]
        elif self.Morphology.Shape == 'Ellipse':
            self.artist.center = self.Position.Position.AsList()

    def GetCellCoords(self):
        #Generates a list of coordinates of rectangle or ellipse shaped cells for use in comparisons between cells using Shapely
        coords=[]
        if self.Morphology.Shape == 'Rectangle':
            rectangle_center = self.Position.Position
            rectangle_size = self.Morphology.Size
            coords.append([rectangle_center.X-0.5*rectangle_size.X,rectangle_center.Y-0.5*rectangle_size.Y])
            coords.append([rectangle_center.X-0.5*rectangle_size.X,rectangle_center.Y+0.5*rectangle_size.Y])
            coords.append([rectangle_center.X+0.5*rectangle_size.X,rectangle_center.Y+0.5*rectangle_size.Y])
            coords.append([rectangle_center.X+0.5*rectangle_size.X,rectangle_center.Y-0.5*rectangle_size.Y])
            coords.append([rectangle_center.X-0.5*rectangle_size.X,rectangle_center.Y-0.5*rectangle_size.Y])

        elif self.Morphology.Shape == 'Ellipse':
            ellipse_center = self.Position.Position
            ellipse_size = self.Morphology.Size
            step = 15
            for angle in range (0,360,step):
                angle_radians = (angle/180)*math.pi
                x = ellipse_center.X + (ellipse_size.X/2)*math.cos(angle_radians)
                y = ellipse_center.Y + (ellipse_size.Y/2)*math.sin(angle_radians)
                coords.append([x,y])
        return coords
    
    def interact (self):
        #simulate interactions with neighbouring cells
        pass

class CellList:
    def __init__(self):
        self.Cells_List=[] 

    def __getitem__(self,index):
        return self.Cells_List[index]

    def FindCell(self, CellID):
        for n,item in enumerate(self.Cells_List):
            if item.ID == CellID:
                return n
            
    def AddCell(self,Cell):
        self.Cells_List.append(Cell)


    def UpdateNeighbours(self, CellID, MaxNeighbourDistance):
        #Uses same algorithm as GetNodeNetwork to find neighbours of a single cell
        #Mostly replaced by UpdateNodeNetwork
        
        self.Cells_List[CellID].Neighbours.clear()
        CellPolygon = shapely.Polygon(self.Cells_List[CellID].Position.Vertices).buffer(MaxNeighbourDistance)
        for n,cell in enumerate(self.Cells_List):
            TestCellPolygon = shapely.Polygon(cell.Position.Vertices)
            Test = CellPolygon.intersection(TestCellPolygon)   
            if (Test.is_empty==False):
                if n!= CellID: self.Cells_List[CellID].Neighbours.append([n,shapely.distance(CellPolygon,TestCellPolygon)])
        
    def GenerateNodeNetwork(self,MaxNeighbourDistance):
        #For each cell in Cells_List, generates a list of the neighbour cells (given MaxNeighbourDistance) and the distance to each
        #of those neighbours.
        # 
        #Data is stored in Cell class in Neihbours as a list of 2D arrays
        #Neighbours[0] gives the index of a Neighbour cell in Cells_List 
        #Neighbours[1] gives the distance of that cell
        for n, cell in enumerate(self.Cells_List):
            #for each cell, loop through all other cells from current cell + 1 and check to see if they interesect
            #generate Shapely.Polygon for current cell (only once)
            CellPolygon = shapely.Polygon(cell.Position.Vertices)

            for i in range(n+1,len(self.Cells_List),1):
                #generate Shapely.Polygon for test cell
                TestCellPolygon = shapely.Polygon(self.Cells_List[i].Position.Vertices)

                #Create polygon containing intersection between the region around cell of interest and test cell
                Distance = shapely.distance(CellPolygon,TestCellPolygon)
                #if polygon contains points, the regions intesersect; add each cell to the other cells network.
                if (Distance < MaxNeighbourDistance):
                    cell.Neighbours.append([i,Distance])
                    self.Cells_List[i].Neighbours.append([n,Distance])

    def UpdateNodeNetwork(self, MaxNeighbourDistance):
        #Requires node network to already be generated (using CellList.GenerateNodeNetwork())
        #similar algorithm to GenerateNodeNetwork, but improves efficiency by only looking for neighbours (~ 30x faster)
        #amongst previous neighbours and neighbours of neighbours. If you're expecting the cell to have moved past 
        #two cells since you last generated the node network, use GenerateNodeNetwork
        for n, cell in enumerate(self.Cells_List):
            cell.Neighbours.clear()
            #for each cell, loop through all other cells from current cell + 1 and check to see if they interesect
            #generate Shapely.Polygon for current cell (only once)
            CellPolygon = shapely.Polygon(cell.Position.Vertices)
            NeighboursOfNeighbours=set()
            for item in cell.Neighbours:
                NeighboursOfNeighbours.add(item[0])
                for neighbour in self[item].Neighbours:
                    NeighboursOfNeighbours.add(neighbour[0])
            
            #print(NeighboursOfNeighbours)

            for neighbour in NeighboursOfNeighbours:
                if neighbour > n:
                #generate Shapely.Polygon for test cell
                    TestCellPolygon = shapely.Polygon(self.Cells_List[neighbour].Position.Vertices)

                    #Create polygon containing intersection between the region around cell of interest and test cell
                    Distance = shapely.distance(CellPolygon,TestCellPolygon)
                    #if polygon contains points, the regions intesersect; add each cell to the other cells network.
                    if Distance <= MaxNeighbourDistance:
                        cell.Neighbours.append([neighbour,Distance])
                        self.Cells_List[neighbour].Neighbours.append([n,Distance])

    def Collision(self,CellID):

        for neighbour in self.Cells_List[CellID].Neighbours:
            MinDistance = self.Cells_List[neighbour[0]].Morphology.Size.X + self.Cells_List[CellID].Morphology.Size.X
            Distance = math.sqrt((self.Cells_List[neighbour[0]].Position.Position.X - self.Cells_List[CellID].Position.Position.X)**2 + (self.Cells_List[neighbour[0]].Position.Position.Y - self.Cells_List[CellID].Position.Position.Y)**2)
            print(CellID,neighbour[0],MinDistance,Distance)
            if Distance <= MinDistance:
                print("Cell",CellID,"crashed into cell",neighbour[0])

        pass
        



    
    






        
