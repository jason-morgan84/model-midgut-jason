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

class Morphology:
    def __init__(self, Shape, Size, Orientation = 0):
        self.Shape = Shape
        self.Size = Size
        self.Orientation = Orientation

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
        self.Position = Position #list giving positon of CENTER of shape in format [x,y]
        self.Morphology = Morphology #class containing information about cells shape and size
        self.Format = Format #class containing information about the cells fill and line colour
        self.Dynamics = Dynamics #class containing information about cell speed and forces applied
        #self.Neighbours = Neighbours #list of XY coordinates of nearby cells 

    def __getitem__(self,index):
        return getattr(self,index)
   
    def Draw(self):
        if self.Morphology.Shape == "Ellipse":
            self.artist = mpatches.Ellipse(
                xy = tuple(self.Position.AsList()),
                width = self.Morphology.Size.X,
                height = self.Morphology.Size.Y,
                fill = True,edgecolor=self.Format.LineColour,
                facecolor = self.Format.FillColour,
                picker = True,
                zorder = 5)
            return self.artist
        
        elif self.Morphology.Shape == "Rectangle":
            self.artist = mpatches.Rectangle(
                xy = tuple([float(self.Position.X - self.Morphology.Size.X/2), self.Position.Y - self.Morphology.Size.Y / 2]),
                width = self.Morphology.Size.X,
                height = self.Morphology.Size.Y,
                fill = True,
                edgecolor = self.Format.LineColour,
                facecolor = self.Format.FillColour,
                picker = True,
                zorder = 5)
            return self.artist
        
    def GetCellCoords(self):
        #Generates a list of coordinates of rectangle or ellipse shaped cells for use in comparisons between cells using Shapely
        coords=[]
        if self.Morphology.Shape == 'Rectangle':
            rectangle_center = self.Position
            rectangle_size = self.Morphology.Size
            coords.append([rectangle_center.X-0.5*rectangle_size.X,rectangle_center.Y-0.5*rectangle_size.Y])
            coords.append([rectangle_center.X-0.5*rectangle_size.X,rectangle_center.Y+0.5*rectangle_size.Y])
            coords.append([rectangle_center.X+0.5*rectangle_size.X,rectangle_center.Y+0.5*rectangle_size.Y])
            coords.append([rectangle_center.X+0.5*rectangle_size.X,rectangle_center.Y-0.5*rectangle_size.Y])
            coords.append([rectangle_center.X-0.5*rectangle_size.X,rectangle_center.Y-0.5*rectangle_size.Y])

        elif self.Morphology.Shape == 'Ellipse':
            ellipse_center = self.Position
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
        CellCoords = self.Cells_List[CellID].GetCellCoords()
        CellPolygon = shapely.Polygon(CellCoords).buffer(MaxNeighbourDistance)

        for n,cell in enumerate(self.Cells_List):
            TestCellCoords = cell.GetCellCoords()
            TestCellPolygon = shapely.Polygon(TestCellCoords)
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
            CellCoords = cell.GetCellCoords()
            CellPolygon = shapely.Polygon(CellCoords)

            for i in range(n+1,len(self.Cells_List),1):
                #generate Shapely.Polygon for test cell
                TestCellCoords = self.Cells_List[i].GetCellCoords()
                TestCellPolygon = shapely.Polygon(TestCellCoords)

                #Create polygon containing intersection between the region around cell of interest and test cell
                Test = CellPolygon.buffer(MaxNeighbourDistance).intersection(TestCellPolygon)

                #if polygon contains points, the regions intesersect; add each cell to the other cells network.
                if (Test.is_empty==False):
                    NodeNetwork[n].append(i)
                    NodeNetwork[i].append(n)


        return NodeNetwork
    






        
