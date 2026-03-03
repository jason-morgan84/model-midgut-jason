#####################################Simulation Initialisation#########################################

import matplotlib.pyplot as plt
import CellClasses, CellVariables, SimulationVariables, CellDynamics
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import math


# Initialises plot area, creates variables storing cell locations and draws cells on plot
# Define plot and axes

def InitialisePlot():
    figure, axes = plt.subplots()
    axes.set_aspect( 1 )
    axes.set_axis_off()
    plt.xlim(0, SimulationVariables.PlotWidth)
    plt.ylim(0, 25)
    #plt.title( 'Drosophila Embryonic Midgut' )
    plt.axvline(x = SimulationVariables.EndPointX * SimulationVariables.PlotWidth, color = 'lightcoral', alpha = 0.5, linewidth = 2, label = 'Finish Line')
    return figure, axes
    
# Initialise CellList variable which will contain a list of all cells with positions, shapes, movement etc.
def InitialiseCells():
    Cells=CellClasses.CellList()
    # For each cell type, intialise starting positions of those cells, add cells to Cells variable and add cell type to legend
    for type in CellVariables.OverallCellTypes:
        for EachCell in type.Initialise():
            Cells.AddCell(EachCell)
    return Cells

def InitialiseLegend(axes):
    LegendPatches=[]
    for type in CellVariables.OverallCellTypes:
        LegendPatches.append(mpatches.Patch(color=type.Format.FillColour, label=type.Name))
    # Adds legend to plot
    plt.legend(handles=LegendPatches, bbox_to_anchor=(0.19, 1.1))
    return axes

def InitialiseScalebar(axes,figure):
    # Add scalebar to plot
    scalebar = AnchoredSizeBar(axes.transData,
                            10*SimulationVariables.Scale, str(SimulationVariables.Scale*10) +'um', loc = 'lower right', 
                            color='royalblue',
                            frameon=False,
                            size_vertical=1,
                            bbox_transform=figure.transFigure,
                            bbox_to_anchor=(0.9, 0.1))
    axes.add_artist(scalebar)
    return axes

#########################################Simulation#########################################
# Simulation function - defines what to do on each tick of the simulation
def Simulate(Cells):
    RecordedPositions = []
    #update network of neighbouring cells
    Cells.GenerateNodeNetwork(1)

    #update forces acting on cells and velocities defined by those forces
    Cells = CellDynamics.UpdateForces(Cells)

    #for each cell, updates position due to calculated velocity and appends cell artist information or positions as required
    #due to simulation types. Updating position is a separate loop to allow all cell velocities to update changing positions.
    for n, cell in enumerate(Cells):
        Cells[n].UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
        RecordedPositions.append([cell.Position.X,cell.Position.Y])
    return Cells, RecordedPositions

def Results(Cells, RecordedPositions):
    # For each cell, calculate average speed in an x direction (overall distance travelled in x / number of ticks) and 
    # average magnitude of the velocity (sum of absolute magnitude of distances travelled each tick / number of ticks)
    DistanceTravelledX = []
    DistanceTravelledTotal = []

    for n, cell in enumerate(Cells):
        StartingPositionX = cell.Position.X
        StartingPositionY = cell.Position.Y
        FinishPositionX = RecordedPositions[len(RecordedPositions)-1][n][0]

        CurrentDistanceTravelledX = abs(FinishPositionX - StartingPositionX)

        CurrentDistanceTravelledTotal = 0
        for m, position in enumerate(RecordedPositions):
            CurrentPositionX = position[n][0]
            CurrentPositionY = position[n][1]
            if m > 0:
                PreviousPositionX = RecordedPositions[m - 1][n][0]
                PreviousPositionY = RecordedPositions[m - 1][n][1]
                CurrentDistanceTravelledTotal += math.hypot(CurrentPositionX - PreviousPositionX,CurrentPositionY - PreviousPositionY)
            elif m == 0:
                CurrentDistanceTravelledTotal = math.hypot(CurrentPositionX - StartingPositionX, CurrentPositionY - StartingPositionY)
            else:
                pass
        print(CurrentDistanceTravelledX,CurrentDistanceTravelledTotal)
        DistanceTravelledX.append(CurrentDistanceTravelledX)
        DistanceTravelledTotal.append(CurrentDistanceTravelledTotal)


    for type in CellVariables.OverallCellTypes:
        # get average speed in x direction and total speed for each cell type
        # consider splitting into only those whose x starting position > 0 to get visible cells only
        print(type.Name)