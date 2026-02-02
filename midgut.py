import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
from matplotlib.backend_bases import MouseButton
import Cell



#TO DO:

#Add change colour of 

#organisation of cells (pack, line etc) as kwargs
#other required details (number of cells, direction, region to pack) as kwargs
#add ability to change packing density


#define plot and axes
figure, axes = plt.subplots()
axes.set_aspect( 1 )
axes.set_axis_off()
plt.xlim(0, 40)
plt.ylim(0, 20)
plt.title( 'Drosophila Embryonic Midgut' )


#define starting positions
VMStartingPositions=[]
VMStartingPositions.append(Cell.StartingPosition(
    ID = "UpperVM",
    Number = 20,
    Position = Cell.XY(1,13.5),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(2,1)),
    DrawOrientation = 'x'))
VMStartingPositions.append(Cell.StartingPosition(
    ID = "LowerVM",
    Number = 20,
    Position = Cell.XY(1,3),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(2,1)),
    DrawOrientation = 'x'))

PMECStartingPositions=[]
PMECStartingPositions.append(Cell.StartingPosition(
    ID = "UpperPMEC",
    Number = 10,
    Position = Cell.XY(0.5,12),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(1,2)),
    DrawOrientation = 'x'))
PMECStartingPositions.append(Cell.StartingPosition(
    ID = "LowerPMEC",
    Number = 10,
    Position = Cell.XY(0.5,4.5),
    Morphology = Cell.Morphology(Shape = 'Rectangle', Size = Cell.XY(1,2)),
    DrawOrientation = 'x'))

OtherStartingPositions=[]
OtherStartingPositions.append(Cell.StartingPosition(
    ID = "Other",
    Number = 20,
    Position = Cell.XY(0.75,6.25),
    Morphology = Cell.Morphology(Shape = 'Ellipse', Size = Cell.XY(1.5,1.5)),
    DrawOrientation = 'pack',
    DrawLimits = Cell.XY(11,11.5)))

#define starting cell types
OverallCellTypes=[]
OverallCellTypes.append(Cell.CellTypes(Name = "VM", StartingPosition = VMStartingPositions, Format = Cell.Format(FillColour = 'plum')))
OverallCellTypes.append(Cell.CellTypes(Name = "PMEC", StartingPosition = PMECStartingPositions, Format = Cell.Format(FillColour = 'powderblue')))
OverallCellTypes.append(Cell.CellTypes(Name = "Other", StartingPosition = OtherStartingPositions, Format = Cell.Format(FillColour = 'palegreen')))

Cells=Cell.CellList()
#initialise cells
for type in OverallCellTypes:
    for position in type.StartingPosition:
            if position.DrawOrientation=='pack':
                #current method only works for circles as test - add in advanced layer algorithm for ellipse packing
                #Dmitrii N. Ilin & Marc Bernacki, 2016, Advancing layer algorithm of dense ellipse packing for generating statistically equivalent polygonal structures
                MaxCellsRow = int((abs(position.DrawLimits.X - position.Position.X)) / position.Morphology.Size.X)
                VertDistance = math.sin(math.pi / 3) * position.Morphology.Size.Y
                MaxRows = int((abs(position.DrawLimits.Y - position.Position.Y)) / VertDistance)
                n = 0
                for y in range(MaxRows):
                    y_position = position.Position.Y + y * VertDistance
                    for x in range(MaxCellsRow):
                        n = n + 1
                        if (y % 2 == 0):
                            x_position = position.Position.X + x * position.Morphology.Size.X
                        else:
                            x_position = position.Position.X + x * position.Morphology.Size.X + position.Morphology.Size.X / 2
                        Cells.AddCell(Cell.Cells(
                            ID = '-'.join((type.Name, position.ID, str(n))),
                            Type = type.Name,
                            Position = Cell.XY(x_position, y_position),
                            Morphology = position.Morphology,
                            Format = type.Format,
                            Dynamics = Cell.Dynamics(Velocity = Cell.XY(0,0), Force = Cell.XY(0,0))))
            else:
                for n in range(position.Number):
                    if position.DrawOrientation == 'x':
                        x_position = position.Position.X + position.Morphology.Size.X * n
                        y_position = position.Position.Y
                    elif position.DrawOrientation == 'y':
                        x_position = position.Position.X
                        y_position = position.Position.Y + position.Morphology.Size.Y * n                        
                    Cells.AddCell(Cell.Cells(
                        ID = '-'.join((type.Name,position.ID,str(n))),
                        Type = type.Name,
                        Position = Cell.XY(float(x_position), float(y_position)),
                        Morphology = position.Morphology,
                        Format = type.Format,
                        Dynamics = Cell.Dynamics(Velocity = Cell.XY(0,0), Force = Cell.XY(0,0))))

for cell in Cells:
    #define velocity of cell
    #if cell.Type == "PMEC" or cell.Type == "Other": cell.Dynamics.Velocity.X = 0.1

    #draw cell
    axes.add_artist(cell.Draw())


# Animation function
def animate(i):
    ArtistList=[]
    for cell in Cells:
        cell.Position.X += cell.Dynamics.Velocity.X
        cell.Position.Y += cell.Dynamics.Velocity.Y
        if cell.Morphology.Shape == 'Rectangle':
            cell.artist.xy = [cell.Position.X-cell.Morphology.Size.X/2,cell.Position.Y-cell.Morphology.Size.Y/2]
        elif cell.Morphology.Shape == 'Ellipse':
            cell.artist.center = cell.Position.AsList()
      
        ArtistList.append(cell.artist)
    return tuple(ArtistList)

ani = animation.FuncAnimation(figure, animate, frames=1000, interval=10, blit=True)

""" def on_click(event):
    if event.button is MouseButton.LEFT:
        print(f'data coords {event.xdata} {event.ydata}') """

def onpick1(event):
    artist=False
    if isinstance(event.artist, mpatches.Rectangle) or isinstance(event.artist, mpatches.Ellipse):
        artist=True
        center = Cell.XY(event.artist.get_center()[0],event.artist.get_center()[1])
        for n, cell in enumerate(Cells):
            if cell.Position.X==center.X and cell.Position.Y==center.Y: 
                Neighbours = Cells.Neighbours(n,1.5)
                print(n, Neighbours)
        for cell in Cells:
            cell.artist.set_edgecolor('black')
        for item in Neighbours:
            Cells[item].artist.set_edgecolor('red')
                    
                    
    if artist==False:
        print("Reset")



#plt.connect('button_press_event', on_click)

figure.canvas.mpl_connect('pick_event', onpick1)

plt.show()






    



