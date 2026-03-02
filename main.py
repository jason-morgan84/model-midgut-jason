import matplotlib.pyplot as plt

import numpy as np
import matplotlib.animation as animation
import math as math
import Cell, CellDynamics, SimulationVariables, CellVariables


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

#1: Add method for measuring results of interest

#2: Add method to change variables by cell type

#3: Tidy method to allow multiple repeats with different variables with single click

#5: Comment Cell.py

#6: Consider changes to adjacency at diagonals
############6.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################6.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent

#7: Improvements to cell arrangement and packing density
############7.1: Custom packing algorithm for circles
##########################7.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
############7.2: Finish "Fill" arrangement 
############7.3: Random variation in cell size

#8: Fix replay mode animation
############8.1: Check if RealTime simulations give different results to Replays and Reports



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

     

# If running in real time, runs simulation and updates output plots
# If running as a replay, runs the simulation through and saves position of each cell at each tick, then draws animation based
# on this saved data.
# If reporting data only, runs simulation and outputs results

if SimulationVariables.SimulationType == "RealTime" or SimulationVariables.SimulationType == "Replay":
    Cells = SimulationVariables.InitialiseCells()
    RecordedPositions=[]
    figure, axes = SimulationVariables.InitialisePlot()
    SimulationVariables.InitialiseLegend(axes)
    SimulationVariables.InitialiseScalebar(axes, figure)
    timer = axes.annotate("0s", xy=(20, 21), xytext=(40,20),horizontalalignment='right',color = 'black')
    for cell in Cells:
        axes.add_artist(cell.Draw())
    plt.ion()

if SimulationVariables.SimulationType == "RealTime":

    for tick in range(SimulationVariables.TickNumber):
        timer.set_text(str(tick*SimulationVariables.TickLength)+"s")
        Cells, NewPosition = Simulate(Cells)
        plt.pause(0.025)

elif SimulationVariables.SimulationType == "Replay":
    for tick in range(SimulationVariables.TickNumber):
        Cells, NewPosition = Simulate(Cells)
        RecordedPositions.append(NewPosition)

    for tick in range(SimulationVariables.TickNumber):
        timer.set_text(str(tick*SimulationVariables.TickLength)+"s")
        for position in RecordedPositions:
            for n, cell in enumerate(position):
                Cells[n].SetPosition(cell[0],cell[1])
        plt.pause(0.025)
           
elif SimulationVariables.SimulationType == "Report":
    for tick in range(SimulationVariables.TickNumber):
        Cells, NewPosition = Simulate(Cells)
        RecordedPositions.append(NewPosition)
  
#calculate results from RecordedPositions

plt.close(figure)

########################################################################################

