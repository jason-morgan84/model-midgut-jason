import matplotlib.patches as mpatches
import shapely.geometry as sg

class XY:
    def __init__(self, X=0, Y=0):
        self.X=X
        self.Y=Y
    
    def AsList(self):
        ClassToList = [self.X,self.Y]
        return ClassToList
    
    def __str__(self):
        return '[' + str(self.X)+', '+str(self.Y)+']'

class CellTypes:
    def __init__(self, Name, StartingPosition, Format):
        self.Name=Name
        self.StartingPosition = StartingPosition
        self.Format=Format

class StartingPosition:
    def __init__(self, ID, Number, Position, Morphology, DrawOrientation = None, DrawLimits=XY(0,0)):
        self.ID = ID #pass identified of starting location
        self.Number = Number #number of cells to be created there
        self.Morphology = Morphology #class containing information about cells shape and size
        self.Position = Position #position of center of first cell as list [x,y]
        self.DrawOrientation = DrawOrientation #should the cells be drawn as a row in x ('x') or as a row in y ('y')
        self.DrawLimits=DrawLimits

class Cells:
    def __init__(self, ID, Type, Position, Morphology, Format, Dynamics):
        self.ID=ID
        self.Type=Type #Type of cell should match an item in CellTypes
        self.Position = Position #list giving positon of CENTER of shape in format [x,y]
        self.Morphology = Morphology #class containing information about cells shape and size
        self.Format = Format #class containing information about the cells fill and line colour
        self.Dynamics = Dynamics #class containing information about cell speed and forces applied

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
                picker = True)
            return self.artist
        
        elif self.Morphology.Shape == "Rectangle":
            self.artist = mpatches.Rectangle(
                xy = tuple([float(self.Position.X - self.Morphology.Size.X/2), self.Position.Y - self.Morphology.Size.Y / 2]),
                width = self.Morphology.Size.X,
                height = self.Morphology.Size.Y,
                fill = True,
                edgecolor = self.Format.LineColour,
                facecolor = self.Format.FillColour,
                picker = True)
            return self.artist

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
        #Looks for cells that are within a rectangle with height and width of those of the cell of interest
        #(defined by its index in Cells_List) multiplied by MaxNeighbourDistance, centred on the center of the cell of interest.

        NeighbourCells=[]
        Cell_Top = self.Cells_List[CellID].Position.Y + (self.Cells_List[CellID].Morphology.Size.Y/2)*MaxNeighbourDistance
        Cell_Bottom = self.Cells_List[CellID].Position.Y - (self.Cells_List[CellID].Morphology.Size.Y/2)*MaxNeighbourDistance
        Cell_Left = self.Cells_List[CellID].Position.X - (self.Cells_List[CellID].Morphology.Size.X/2)*MaxNeighbourDistance
        Cell_Right = self.Cells_List[CellID].Position.X + (self.Cells_List[CellID].Morphology.Size.X/2)*MaxNeighbourDistance
 
        for n,cells in enumerate(self.Cells_List):
            Test_Cell_Top = cells.Position.Y + cells.Morphology.Size.Y/2
            Test_Cell_Bottom = cells.Position.Y - cells.Morphology.Size.Y/2
            Test_Cell_Left = cells.Position.X - cells.Morphology.Size.X/2
            Test_Cell_Right = cells.Position.X + cells.Morphology.Size.X/2
            Test = sg.box(Cell_Left,Cell_Bottom,Cell_Right,Cell_Top).intersection(sg.box(Test_Cell_Left,Test_Cell_Bottom,Test_Cell_Right,Test_Cell_Top))
            if(str(Test)!="POLYGON EMPTY"): 
                if n!= CellID: NeighbourCells.append(n)

        #multiply size of cell by maxneighbourdistance, find all other cells with center within this range
        return NeighbourCells
    
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





        
