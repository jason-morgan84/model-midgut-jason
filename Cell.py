import matplotlib.patches as mpatches
import math
import time
import numpy as np

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
                    WidthToFill = (abs(position.DrawLimits.X - position.Position.X))
                    HeightToFill = (abs(position.DrawLimits.Y - position.Position.Y))
                    MaxCellsRow = int(WidthToFill / ((position.Morphology.Radius*2)/position.Density))
                    VertDistance = (math.sin(math.pi / 3) * position.Morphology.Radius*2) / position.Density
                    MaxRows = int(HeightToFill / VertDistance)
                    n = 0
                    for y in range(MaxRows):
                        y_position = position.Position.Y + y * VertDistance + (HeightToFill - MaxRows * VertDistance) / 2
                        for x in range(MaxCellsRow):
                            n = n + 1
                            if (y % 2 == 0):
                                x_position = position.Position.X + x * (2*position.Morphology.Radius/position.Density)
                            else:
                                x_position = position.Position.X + x * (2*position.Morphology.Radius/position.Density) + position.Morphology.Radius
                            NewCell = Cells(
                                ID = '-'.join((self.Name, position.ID, str(n))),
                                Type = self.Name,
                                Position = XY(x_position, y_position),
                                Morphology = position.Morphology,
                                Format = self.Format,
                                Dynamics = Dynamics(Velocity = XY(0,0), AppliedForce = XY(0,0), InternalForce = XY(0,0)),
                                Neighbours=[])    
                            OutputCellList.append(NewCell)
            elif position.Arrange == 'XAlign' or position.Arrange == 'YAlign':
                for n in range(position.Number):
                    if position.Arrange == 'XAlign':
                        x_position = position.Position.X + (2 * position.Morphology.Radius)* n
                        y_position = position.Position.Y
                    elif position.Arrange == 'YAlign':
                        x_position = position.Position.X
                        y_position = position.Position.Y + 2 * position.Morphology.Radius * n                   

                    NewCell=Cells(
                        ID = '-'.join((self.Name,position.ID,str(n))),
                        Type = self.Name,
                        Position = XY(x_position, y_position),
                        Morphology = position.Morphology,
                        Format = self.Format,
                        Dynamics = Dynamics(Velocity = XY(0,0), AppliedForce = XY(0,0), InternalForce = XY(0,0)),
                        Neighbours=[])
                    #NewCell.Position.Vertices = NewCell.GetCellCoords()                   
                    OutputCellList.append(NewCell)
            else:
                x_position = position.Position.X
                y_position = position.Position.Y
                NewCell = Cells(
                    ID = '-'.join((self.Name,position.ID)),
                    Type = self.Name,
                    Position = XY(x_position, y_position),
                    Morphology = position.Morphology,
                    Format = self.Format,
                    Dynamics = Dynamics(Velocity = XY(0,0), AppliedForce = XY(0,0), InternalForce = XY(0,0)),
                    Neighbours=[])
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

class Morphology:
    def __init__(self, Radius):
        self.Radius = Radius
        
class Format:
    def __init__(self, FillColour='White', LineColour='Black', LineWidth=1):
        self.FillColour=FillColour
        self.LineColour = LineColour
        self.LineWidth = LineWidth

class Dynamics:
    # This class defines the forces applied to a cell leading to a given Velocity.
    # Each is defined as an XY class giving an x-component and y-component of each vector.
    # Cells experience applied forces from their neighbours and environment (applied force)
    # and an internal force caused by the cells own activities.
    # These forces generate acceleration (in proportion to the cells radius (and density, but currently this is assumed to be constant between cells))
    # and this acceleration leads to a change in Velocity, also stored as a vector in xy component form.
    def __init__(self, AppliedForce=XY(0,0), InternalForce = XY(0,0), Velocity=XY(0,0)):
        self.AppliedForce = AppliedForce
        self.InternalForce = InternalForce
        self.Velocity=Velocity

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
        self.artist = mpatches.Circle(
            xy = self.Position.AsTuple(),
            radius = self.Morphology.Radius,
            fill = True,edgecolor=self.Format.LineColour,
            facecolor = self.Format.FillColour,
            picker = True,
            zorder = 5)
        return self.artist
        
   
    def UpdatePosition(self,XChange,YChange):
        self.Position.X += XChange
        self.Position.Y += YChange

        self.artist.center = self.Position.AsList()


    def SetPosition(self,X,Y):
        self.Position.X = X
        self.Position.Y = Y
 
        self.artist.center = self.Position.AsList()

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
        
    def N(self,CellTypes = "All"):
        n = 0
        if CellTypes == "All":
            for item in self:
                n += 1
        else:
            for item in self:
                for celltype in CellTypes:
                    if item.Type == celltype: 
                        n += 1
        return n
       
    def GenerateNodeNetwork(self,MaxNeighbourDistance):
        #For each cell in Cells_List, generates a list of the neighbour cells (given MaxNeighbourDistance) and the distance to each
        #of those neighbours.
        # 
        #Data is stored in Cell class in Neihbours as a list of 2D arrays
        #Neighbours gives the index of a Neighbour cell in Cells_List 
        [cell.Neighbours.clear() for cell in self.Cells_List]
        for n, cell in enumerate(self.Cells_List):

            #for each cell, loop through all other cells from current cell + 1 and check to see if they interesect
            for i in range(n + 1, len(self.Cells_List), 1):
                #Calculate distance between cells: distance between centres subtract the two radiuseses
                Distance = math.sqrt((cell.Position.X-self.Cells_List[i].Position.X)**2 + (cell.Position.Y-self.Cells_List[i].Position.Y)**2) - cell.Morphology.Radius - self.Cells_List[i].Morphology.Radius
                #if polygon contains points, the regions intesersect; add each cell to the other cells network.
                if (Distance < MaxNeighbourDistance):
                    cell.Neighbours.append(i)
                    self.Cells_List[i].Neighbours.append(n)
      










    
    






        
