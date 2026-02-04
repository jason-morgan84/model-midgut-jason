import matplotlib.patches as mpatches
import shapely.geometry as sg
import math
import shapely

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
                            NewCell = Cells(
                                ID = '-'.join((self.Name, position.ID, str(n))),
                                Type = self.Name,
                                Position = Position(XY(x_position, y_position)),
                                Morphology = position.Morphology,
                                Format = self.Format,
                                Dynamics = Dynamics(Velocity = XY(0,0), Force = XY(0,0)))
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
                        Position = Position(XY(x_position, y_position)),
                        Morphology = position.Morphology,
                        Format = self.Format,
                        Dynamics = Dynamics(Velocity = XY(0,0), Force = XY(0,0)))
                    NewCell.Position.Vertices = NewCell.GetCellCoords()                   
                    OutputCellList.append(NewCell)
            else:
                x_position = position.Position.X
                y_position = position.Position.Y
                NewCell = Cells(
                    ID = '-'.join((self.Name,position.ID)),
                    Type = self.Name,
                    Position = Position(XY(x_position, y_position)),
                    Morphology = position.Morphology,
                    Format = self.Format,
                    Dynamics = Dynamics(Velocity = XY(0,0), Force = XY(0,0)))
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
    def __init__(self, Position, Vertices=[], Orientation = 0):
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
    def __init__(self, ID, Type, Position, Morphology, Format, Dynamics):
        self.ID=ID
        self.Type=Type #Type of cell should match an item in CellTypes
        self.Position = Position #Class containing information about cells position, orientation. Also stores coords of vertices.
        self.Morphology = Morphology #class containing information about cells shape and size
        self.Format = Format #class containing information about the cells fill and line colour
        self.Dynamics = Dynamics #class containing information about cell speed and forces applied
        #self.Neighbours = Neighbours #list of XY coordinates of nearby cells 

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
        self.position.Coords = self.GetCellCoords()
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


    def Neighbours(self, CellID, MaxNeighbourDistance):
        #Uses same algorithm as GetNodeNetwork to find neighbours of a single cell
        #Mostly replaced by GetNodeNetwork

        NeighbourCells=[]
        CellPolygon = shapely.Polygon(self.Cells_list[CellID].Position.Vertices).buffer(MaxNeighbourDistance)

        for n,cell in enumerate(self.Cells_List):
            TestCellPolygon = shapely.Polygon(cell.Position.Vertices)
            Test = CellPolygon.intersection(TestCellPolygon)   
            if (Test.is_empty==False):
                if n!= CellID: NeighbourCells.append(n)
        return NeighbourCells
    
    def GetNodeNetwork(self,MaxNeighbourDistance):
        #Node network is a list of lists of length number of cells
        NodeNetwork = [[] for _ in range(len(self.Cells_List))]

        for n, cell in enumerate(self.Cells_List):
            #for each cell, loop through all other cells from current cell + 1 and check to see if they interesect
            #generate Shapely.Polygon for current cell (only once)
            CellPolygon = shapely.Polygon(cell.Position.Vertices)

            for i in range(n+1,len(self.Cells_List),1):
                #generate Shapely.Polygon for test cell
                TestCellPolygon = shapely.Polygon(self.Cells_List[i].Position.Vertices)

                #Create polygon containing intersection between the region around cell of interest and test cell
                Test = CellPolygon.buffer(MaxNeighbourDistance).intersection(TestCellPolygon)

                #if polygon contains points, the regions intesersect; add each cell to the other cells network.
                if (Test.is_empty==False):
                    NodeNetwork[n].append(i)
                    NodeNetwork[i].append(n)


        return NodeNetwork
    






        
