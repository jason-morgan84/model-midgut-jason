#######################################Key Simulation Variables#######################################
PlotWidth = 40                  #   Width of simulation in plot units
Scale = 1                       #   Size of 1 plot unit in um
TickLength = 1                  #   Length of simulation tick in seconds
TickNumber = 30               #   Length of simulation in ticks
SpeedLimit = 0.06               #   Maximum allowed speed of cells (plot unit/tick)
SimulationType = "RealTime"       #   Simulate in real time ("RealTime"), simulate then replay ("Replay") or just report results ("Report")

#Variables defining speed of migration
MigrationSpeed = 0.05           #   Speed of migrating cells (plot unit/tick)
MigrationForce = 0.005           #   Force applied to a migrating cell

#Variables defining adhesion
AdhesionDistance = 0.05         #   Distance of two adhered cells (plot unit)
AdhesionForceDistance = AdhesionDistance * 3    #   Maximum distance beyond cell boundary that adhesion forces are felt
AdhesionForce = 0.001            #   Maximum force adhesion applies to neighbouring cells (MassUnits.ScaleUnits.TickLength^-2)

#Variables defining repulsion (collision avoidance)
MinimumDesiredGap = 0.1        #   Minimum desired gap between cells (gaps can be smaller than this, but repulsive force will increase)
ProximityForce = 0.05        #   Maximum repulsive force on cells

# Variables for cell intrinsic forces (the force a cell applies to itself to go where it 'wants' to go)
InternalForce = 0.005           #   Maximum force a cell can apply to itself
Directionality = 0              #   Tendency of a cell to maintain a specific direction (1 - straight line, 0 - random direction)

#Variables that define  simulation end point
EndPointX = 0.75                 #   Defines 'finish line' in terms of width of simulation
FinishProportion = 0.5          #   Proportion of cells to have passed EndPointX for simulation to be considered over

#####################################Simulation Initialisation#########################################


import matplotlib.pyplot as plt
import Cell, CellVariables, SimulationVariables
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar


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
    Cells=Cell.CellList()
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