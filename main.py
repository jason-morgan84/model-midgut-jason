import matplotlib.pyplot as plt
import math as math
import SimulationVariables, Simulation


# Main program loop
# Uses CellClasses.py for:
#       Classes defining cell types, properties and starting locations
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
# Uses CellVariables.py to define the cell types, their properties and their starting locations
#
# Uses SimulationVariables.py to define key constants governing the plot area, simulation and interactions between cells
#
# Uses Simulation.py to define main simulation loop and result calculation


#TO DO:

#1: Is there some way to avoid oscilations and bouncing apart in nearby cells - adhesion pulls them together then repulsion pushes them apart

#2: Add starting positions to data recorded for each cell
############2.2: Update calculation of results to use this new data

#3: Add method to allow multiple repeats with different variables with single click

#4: Adjust animations to allow interaction during pauses

#5: Comment CellClasses.py
############5.2: Add workflow to comments above

#6: Consider changes to adjacency at diagonals
############6.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################6.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent

#7: Improvements to cell arrangement and packing density
############7.1: Custom packing algorithm for circles
##########################7.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
############7.2: Finish "Fill" arrangement 
############7.3: Random variation in cell size

#####################################################################################################################################





Cells = Simulation.InitialiseCells()
RecordedPositions=[]

# If running in real time or replay, sets up plot for animations
if SimulationVariables.SimulationType == "RealTime" or SimulationVariables.SimulationType == "Replay":
    figure, axes = Simulation.InitialisePlot()
    Simulation.InitialiseLegend(axes)
    Simulation.InitialiseScalebar(axes, figure)
    timer = axes.annotate("0s", xy=(20, 21), xytext=(40,20),horizontalalignment='right',color = 'black')
    for cell in Cells:
        axes.add_artist(cell.Draw())
    plt.ion()

# If running in real time, runs simulation, saves position of each cell at each tick and updates output plots
if SimulationVariables.SimulationType == "RealTime":
    for tick in range(SimulationVariables.TickNumber):
        timer.set_text(str(tick*SimulationVariables.TickLength) + "s")
        Cells = Simulation.Simulate(Cells)
        NewPosition = []
        for cell in Cells:
            NewPosition.append([cell.Position.X,cell.Position.Y])
            cell.UpdateArtist()
        RecordedPositions.append(NewPosition)
        plt.pause(0.025)

# If running as a replay, runs the simulation through and saves position of each cell at each tick, then draws animation based
# on this saved data.
elif SimulationVariables.SimulationType == "Replay":
    for tick in range(SimulationVariables.TickNumber):
        Cells = Simulation.Simulate(Cells)
        NewPosition = []
        for cell in Cells:
            NewPosition.append([cell.Position.X,cell.Position.Y])
        RecordedPositions.append(NewPosition)
      
    for tick, position in enumerate(RecordedPositions):
        timer.set_text(str(tick*SimulationVariables.TickLength)+"s")
        for n, cell in enumerate(position):
            Cells[n].SetPosition(position[n][0],position[n][1],True)
        plt.pause(0.025)

# If reporting data only, runs simulation and saves positin of each cell at each tick
elif SimulationVariables.SimulationType == "Report":
    for tick in range(SimulationVariables.TickNumber):
        Cells = Simulation.Simulate(Cells)
        NewPosition = []
        for cell in Cells:
            NewPosition.append([cell.Position.X,cell.Position.Y])
        RecordedPositions.append(NewPosition)

#calculate results from RecordedPositions and starting positions
Simulation.Results(Simulation.InitialiseCells(), RecordedPositions)



########################################################################################

