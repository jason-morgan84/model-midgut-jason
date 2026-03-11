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
#
#
# 1: Initialises list of all cells by creating cells of each cell type defined in CellVariables.py
# 2: Initialises plot for animation (if required)
# 3: Draws cells (if required)
# 4: Carries out simulation for number of ticks defined in SimulationVariables.py
# 5: For each tick:
######## - Calculates neighbouring cells for each cell
######## - Calculates forces applied to cell by itself and its neighbours (in x and y components)
######## - Calculates overall acceleartion applied to cell (in x and y components)
######## - Calculates velocity of each cell (in x and y components)
# 6: Moves cell to new position (once forces/acceleration/velocity have been calculated for ALL cells in current position)
# 7: Updates actor positions (if required)
# 8: For each cell, gets its new position and adds it to record of positions of each cell for each tick
# 9: After simulation, uses recorded positions to calculate measurements of interest


#TO DO:

#1: Is there some way to avoid oscilations and bouncing apart in nearby cells - adhesion pulls them together then repulsion pushes them apart

#4: Adjust animations to allow interaction during pauses

#5: Comment CellClasses.py
############5.1: Add workflow to comments above
############5.2: Finsih comments in Simulation function

#6: Consider changes to adjacency at diagonals
############6.2: For adjacency, consider cell at 45 degrees but slightly further due to packing as just as adjacent as one as 90 degrees?
##########################6.2.1: But one at 45 degrees an absolutely adjacent is not closer than one at 90 degrees and adjacent

#7: Improvements to cell arrangement and packing density
############7.1: Custom packing algorithm for circles
##########################7.1.1: Remember, circles are only acting as models for cells - no need for complexity provided by ellipses
############7.2: Finish "Fill" arrangement 
############7.3: Random variation in cell size

#####################################################################################################################################


import Simulation, SimulationVariables, CellVariables

Repeats = 3

#adhesion force 0.0001,0.0005,0.001, 0.005, 0.01,0.05,0.1
#migration speed 0.0005, 0.001, 0.005, 0.01,0.05,0.1
#internal force 0.05,0.01,0.005

migration_speeds = [0.0005, 0.001, 0.005, 0.01,0.05,0.1]
adhesion_force_others = [0.0001,0.0005,0.001, 0.005, 0.01,0.05,0.1]
adhesion_force_pmec_multiples = [0.75,1,1.5,2]
internal_forces = [0.001, 0.005, 0.01, 0.05, 0.1]
print("migration_speed,adhesion_force_other,adhesion_force_pmec_multiple,internal_force,repeat,type,average_speed_x,average_speed_total")

for migration_speed in migration_speeds:
    SimulationVariables.MigrationSpeed = migration_speed
    for adhesion_force in adhesion_force_others:
        CellVariables.OverallCellTypes[2].Interactions.InternalForce = adhesion_force
        for multiple in adhesion_force_pmec_multiples:
            CellVariables.OverallCellTypes[0].Interactions.AdhesionForce = adhesion_force * multiple
            for internal_force in internal_forces:
                CellVariables.OverallCellTypes[0].Interactions.InternalForce = internal_force
                CellVariables.OverallCellTypes[2].Interactions.InternalForce = internal_force
                for i in range (Repeats):

                    Cells = Simulation.InitialiseCells()
                    Cells, RecordedPositions = Simulation.Simulate(Cells)
                    Results = Simulation.Results(Cells, RecordedPositions)

                    for item in Results:
                        print(migration_speed,adhesion_force,multiple,internal_force,i,item[0],(item[2]/item[1])/(SimulationVariables.TickNumber*SimulationVariables.TickLength),(item[3]/item[1])/(SimulationVariables.TickNumber*SimulationVariables.TickLength))

            