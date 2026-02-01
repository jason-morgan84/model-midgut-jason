import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
from matplotlib.backend_bases import MouseButton

class CellTypes:
    def __init__(self, name, shape, StartingPosition,colour='white'):
        self.Name=name
        self.Shape = shape
        self.StartingPosition = StartingPosition
        self.colour=colour

        
class StartingPosition:
    def __init__(self,ID,Number,Size,Position,CellOrientation=0,DrawOrientation=None,DrawLimits=[0,0]):
        self.ID = ID #pass identified of starting location
        self.Number = Number #number of cells to be created there
        self.Size = Size #size of cells as list [x,y]
        self.Position = Position #position of center of first cell as list [x,y]
        self.CellOrientation = CellOrientation #rotation of cell in degrees (defaults to 0)
        self.DrawOrientation = DrawOrientation #should the cells be drawn as a row in x ('x') or as a row in y ('y')
        self.DrawLimits=DrawLimits


class Cell:
    def __init__(self, ID, Type, Shape, Position, Size, colour='white',Velocity=[0,0]):
        self.ID=ID
        self.Type=Type #Type of cell should match an item in CellTypes
        self.Position = Position #list giving positon of CENTER of shape in format [x,y]
        self.Shape = Shape #'rectangle' or 'ellipse'
        self.Size = Size #list of size in the format [x_size,y_size]
        self.colour=colour
        self.Velocity=Velocity #velocity of cell in the format [x,y] - defaults to 0

    def Draw(self):
        if self.Shape == "ellipse":
            self.artist = mpatches.Ellipse(tuple(self.Position),self.Size[0],self.Size[1],fill=True,edgecolor='black',facecolor=self.colour)
            return self.artist
        
        elif self.Shape == "rectangle":
            self.artist = mpatches.Rectangle(tuple([self.Position[0]-self.Size[0]/2,self.Position[1]-self.Size[1]/2]),self.Size[0],self.Size[1],fill=True,edgecolor='black',facecolor=self.colour)
            return self.artist
        
    def Neighbours(Self,CellID,CellList,MaxNeighbourDistance):
        NeighbourCells=[]
        #consider converting cell list to dictionary to ease searching
        #should this be within class cell or not
        #multiply size of cell by maxneighbourdistance, find all other cells with center within this range
        return NeighbourCells



#define plot and axes
figure, axes = plt.subplots()
axes.set_aspect( 1 )
axes.set_axis_off()
plt.xlim(0, 40)
plt.ylim(0, 20)
plt.title( 'Drosophila Embryonic Midgut' )


#define starting positions
VMStartingPositions=[]
VMStartingPositions.append(StartingPosition("UpperVM",20,[2,1],[1,13.5],0,'x'))
VMStartingPositions.append(StartingPosition("LowerVM",20,[2,1],[1,3],0,'x'))
PMECStartingPositions=[]
PMECStartingPositions.append(StartingPosition("UpperPMEC",10,[1,2],[0.5,12],0,'x'))
PMECStartingPositions.append(StartingPosition("LowerPMEC",10,[1,2],[0.5,4.5],0,'x'))
OtherStartingPositions=[]
OtherStartingPositions.append(StartingPosition("Other",20,[1.5,1.5],[0.75,6.25],0,'pack',[11,11.5]))

#define starting cell types
OverallCellTypes=[]
OverallCellTypes.append(CellTypes("VM",'rectangle',VMStartingPositions,colour='plum'))
OverallCellTypes.append(CellTypes("PMEC",'rectangle',PMECStartingPositions,colour='powderblue'))
OverallCellTypes.append(CellTypes("Other",'ellipse',OtherStartingPositions,colour='palegreen'))


Cells=[]
#initialise cells
for type in OverallCellTypes:
    for position in type.StartingPosition:
            if position.DrawOrientation=='pack':
                #current method only works for circles as test - add in advanced layer algorithm for ellipse packing
                #Dmitrii N. Ilin & Marc Bernacki, 2016, Advancing layer algorithm of dense ellipse packing for generating statistically equivalent polygonal structures
                MaxCellsRow = int((abs(position.DrawLimits[0]-position.Position[0]))/position.Size[0])
                VertDistance = math.sin(math.pi/3)*position.Size[1]
                MaxRows = int((abs(position.DrawLimits[1]-position.Position[1]))/VertDistance)
                n=0
                for y in range(MaxRows):
                    y_position=position.Position[1]+y*VertDistance
                    for x in range(MaxCellsRow):
                        n=n+1
                        if (y%2==0):
                            x_position=position.Position[0]+x*position.Size[0]
                        else:
                            x_position=position.Position[0]+x*position.Size[0]+position.Size[0]/2
                        Cells.append(Cell(ID=type.Name+position.ID+str(n),
                            Type=type.Name,
                            Shape=type.Shape,
                            Position = [x_position, y_position],
                            Size = position.Size,
                            colour=type.colour))
            else:
                for n in range(position.Number):
                    if position.DrawOrientation=='x':
                        x_position = position.Position[0]-position.Size[0]/2+position.Size[0]*n
                        y_position = position.Position[1]-position.Size[1]/2
                    elif position.DrawOrientation=='y':
                        x_position = position.Position[0]-position.Size[0]/2
                        y_position = position.Position[1]-position.Size[1]/2+position.Size[1]*n                        
                    Cells.append(Cell(ID=type.Name+position.ID+str(n),
                        Type=type.Name,
                        Shape=type.Shape,
                        Position = [x_position, y_position],
                        Size = position.Size,
                        colour=type.colour))

for cell in Cells:
    #define velocity of cell
    #if cell.Type == "PMEC" or cell.Type == "Other": cell.Velocity=[0.1,0]

    #draw cell
    axes.add_artist(cell.Draw())

# Animation function
def animate(i):
    ArtistList=[]
    for cell in Cells:
        cell.Position[0]=cell.Position[0]+cell.Velocity[0]
        cell.Position[1]=cell.Position[1]+cell.Velocity[1]
        if cell.Shape=='rectangle':
            cell.artist.xy=[cell.Position[0],cell.Position[1]]
        elif cell.Shape=='ellipse':
            cell.artist.center=[cell.Position[0],cell.Position[1]]
      
        ArtistList.append(cell.artist)
    return tuple(ArtistList)

ani = animation.FuncAnimation(figure, animate, frames=1000, interval=10, blit=True)

def on_click(event):
    if event.button is MouseButton.LEFT:
        print(f'data coords {event.xdata} {event.ydata}')



plt.connect('button_press_event', on_click)

plt.show()






    



