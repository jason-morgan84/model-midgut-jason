import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import matplotlib.text
import math as math
import Cell, CellDynamics, SimulationVariables, CellVariables
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

# Main program loop
# Uses Cell.py for:
#       Classes defining cell types
#       Classes defining cell starting locations
#       Classes defining individual cell properties
#       Functions for adding cells, updating their properties and defining neighbouring cells
#       Functions for defining artist variables for drawing using MatPlotLib
# 
# Uses CellDynamics.py for functions defining forces acting on cells during simulations, including:
#       Adhesive forces
#       Repulsive forces (to control cell collisions/overlap)
#       Forces due to signalling from neighbouring cells
#       Cell intrinsic forces (where does the cell want to go?)
#       Drag forces
#
# Uses CellVariables.py to define the cell types and their starting locations
#
# Uses SimulationVariables.py to define key constants governing the plot area, simulation and interactions between cells


#TO DO:
#-1: What if adhesion also effects the direction the cells want to move in?

#0: Add method to allow multiple repeats with different variables with single click

#1: Add method for measuring results of interest

#2: Comment Cell.py

#3: Consider changes to adjacency at diagonals
############3.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################3.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent

#5: Improvements to cell arrangement and packing density
############5.1: Custom packing algorithm for circles
##########################5.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
############5.2: Finish "Fill" arrangement 
############5.3: Random variation in cell size

#6: Why do RealTime simulations give different results to Replays and Reports


#####################################Initialisation#####################################
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
    
    # Defines neighbours for each cell
    Cells.GenerateNodeNetwork(1)

    # Draw each cell on axis

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
def Simulate(i):
    global Finished
    global EndTime
    global Cells
    global FinishedCells
    global FinishedOtherCells
    global FinishedPMECCells

    ArtistList=[]
    OutputPositions=[]
    FinishedCells = 0 
    FinishedPMECCells = 0
    FinishedOtherCells = 0
    #update network of neighbouring cells
    Cells.GenerateNodeNetwork(1)

    #update forces acting on cells and velocities defined by those forces
    Cells = CellDynamics.UpdateForces(Cells)

    #for each cell, updates position due to calculated velocity and appends cell artist information or positions as required
    #due to simulation types. Updating position is a separate loop to allow all cell velocities to update changing positions.
    for n, cell in enumerate(Cells):
        Cells[n].UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
        if SimulationVariables.SimulationType == "RealTime": 
            ArtistList.append(cell.artist)
        elif SimulationVariables.SimulationType == "Replay":
            OutputPositions.append([cell.Position.X,cell.Position.Y])
        else:
            pass

        #count number of cells that have passed the finish line

        if cell.Position.X > (SimulationVariables.PlotWidth * SimulationVariables.EndPointX) and cell.Type != "VM":
            if cell.Type == "Other":
                FinishedOtherCells += 1
            elif cell.Type == "PMEC":
                FinishedPMECCells += 1
            FinishedCells = FinishedPMECCells + FinishedOtherCells
        NCells = n
    #NCells = Cells.N()

    #if finishing requirements are met, set simulation as finished and save end time
    if FinishedCells >= NCells * SimulationVariables.FinishProportion and Finished == False:
        Finished = True
        EndTime = i * SimulationVariables.TickLength
    


    #update timer - if not finished, increment by ticklength, if finished, set to end time
    if Finished == False:
        timer.set_text(str(i * SimulationVariables.TickLength) + "s")
    else:
        timer.set_text(str(EndTime) + "s")
        timer.set_color('r')

    #update counter for cells that have reached finish requirements
    counter.set_text(str(FinishedCells)+"/"+str(int(round(NCells*SimulationVariables.FinishProportion))))
    
    #return artist list for real time simulation
    if SimulationVariables.SimulationType == "RealTime":
        ArtistList.append(timer)
        ArtistList.append(counter)
        return tuple(ArtistList)
    
    #return positions for replayed simulation
    elif SimulationVariables.SimulationType == "Replay":
        return OutputPositions


#########################################Replay#########################################
# Replay function - if not being run in real time, goes through each saved position and moves cells accordingly
def Replay(i):
    ArtistList=[]
    for n, CellPosition in enumerate(RecordedPositions[i]):
        Cells[n].SetPosition(CellPosition[0],CellPosition[1])
        ArtistList.append(Cells[n].artist)
    timer.set_text(str(i*SimulationVariables.TickLength)+"s")
    ArtistList.append(timer)
    return tuple(ArtistList)

######################################Interaction#######################################
# What to do on mouse click - only works when running in real time
def onpick1(event):
    if isinstance(event.artist, mpatches.Rectangle) or isinstance(event.artist, mpatches.Ellipse):
        for cell in Cells:
            cell.artist.set_edgecolor('black')
        center = Cell.XY(event.artist.get_center()[0],event.artist.get_center()[1])
        for n, cell in enumerate(Cells):
            if cell.Position.X==center.X and cell.Position.Y==center.Y: 
                #cell.Dynamics.Velocity.X = (np.random.random()-0.5)*0.5
                #cell.Dynamics.Velocity.Y = (np.random.random()-0.5)*0.5
                #print(cell.Neighbours)
                for item in cell.Neighbours:
                    Cells[item].artist.set_edgecolor('red')     
    else:
        for cell in Cells:
            cell.artist.set_edgecolor('black')
            

# If running in real time, runs simulation and updates output plots
# If running as a replay, runs the simulation through and saves position of each cell at each tick, then draws animation based
# on this saved data.
# If reporting data only, runs simulation and outputs results

Repeats = 1
#MigrationForces = [0.1,0.05,0.01,0.005]
#AdhesionForces = [0.0001,0.0005,0.001,0.005,0.01,0.05]
#InternalForces = [0.0001,0.0005,0.001,0.005,0.01,0.05]   

MigrationForces = [0.1]
AdhesionForces = [0.2]
InternalForces = [0.05]   

print("InternalForce, MigrationForce, AdhesionForce, Repeat, FinishedPMECCells, TotalPMECCells, FinishedOtherCells, TotalOtherCells")
for InternalForce in InternalForces:
    SimulationVariables.InternalForce = InternalForce
    for MigrationForce in MigrationForces:
        SimulationVariables.MigrationForce = MigrationForce
        for AdhesionForce in AdhesionForces:
            SimulationVariables.AdhesionForce = AdhesionForce
            for repeat in range(Repeats):
                figure, axes = InitialisePlot()
                Cells = InitialiseCells()
                InitialiseLegend(axes)
                InitialiseScalebar(axes, figure)

                # Adds finish line, finish counter and timer to plot
                global Finished
                global EndTime 
                global FinishedOtherCells
                global FinishedPMECCells

                EndTime = SimulationVariables.TickNumber                     
                Finished = False
                FinishedOtherCells = 0
                FinishedPMECCells = 0

                for cell in Cells:
                    axes.add_artist(cell.Draw())

                timer = axes.annotate("0s", xy=(20, 21), xytext=(40,20),horizontalalignment='right',color = 'black')
                counter = axes.annotate("0/"+str(int(round(Cells.N() * SimulationVariables.FinishProportion,0))), xy=(20, 21), xytext=(40,1), horizontalalignment='right')



                if SimulationVariables.SimulationType == "RealTime":
                    ani = animation.FuncAnimation(figure, func = Simulate, frames=SimulationVariables.TickNumber, interval=40, blit=True,repeat=False)

                elif SimulationVariables.SimulationType == "Replay":
                    RecordedPositions=[]
                    for tick in range(SimulationVariables.TickNumber):
                        if Finished == False:
                            NewPosition = Simulate(tick)
                            RecordedPositions.append(NewPosition)
                        else:
                            break
                    ani = animation.FuncAnimation(figure, Replay, frames=len(RecordedPositions), interval=10, blit=True, repeat=False)

                elif SimulationVariables.SimulationType == "Report":
                    for tick in range(SimulationVariables.TickNumber):
                        Simulate(tick)
                    print(InternalForce,MigrationForce, AdhesionForce, repeat, FinishedPMECCells, Cells.N("PMEC"),FinishedOtherCells,Cells.N("Other"))
                    #print("Adhesion Force: " + str(SimulationVariables.AdhesionForce) + ": "+ str(FinishedCells)+" cells covered "
                    #              +str(SimulationVariables.EndPointX * SimulationVariables.PlotWidth)+"uM in " + str(EndTime) + "s")


        

                if SimulationVariables.SimulationType == "RealTime": figure.canvas.mpl_connect('pick_event', onpick1)
                if SimulationVariables.SimulationType != "Report": plt.show()
                plt.close(figure)

########################################################################################

