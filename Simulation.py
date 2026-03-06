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
    Cells = CellClasses.CellList()
    # For each cell type, intialise starting positions of those cells, add cells to Cells variable and add cell type to legend
    for type in CellVariables.OverallCellTypes:
        for cell in type.Initialise():
            Cells.AddCell(cell)
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





#########################################Results Calculation#########################################
def Results(Cells, RecordedPositions):
    # For each cell, calculate average speed in an x direction (overall distance travelled in x / number of ticks) and 
    # average magnitude of the velocity (sum of absolute magnitude of distances travelled each tick / number of ticks)
    DistanceTravelledX = []
    DistanceTravelledTotal = []

    for n, cell in enumerate(Cells):
        StartingPositionX = cell.StartingPosition.X
        StartingPositionY = cell.StartingPosition.Y
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
        DistanceTravelledX.append(CurrentDistanceTravelledX)
        DistanceTravelledTotal.append(CurrentDistanceTravelledTotal)

    Results=[]
    for type in CellVariables.OverallCellTypes:
        nType = 0
        TotalTravelledX = 0
        TotalTravelledTotal = 0
        # get average speed in x direction and total speed for each cell type
        # consider splitting into only those whose x starting position > 0 to get visible cells only
        for n, cell in enumerate(Cells):
            if cell.Type == type.Name and cell.StartingPosition.X > 0:
                nType += 1
                TotalTravelledX += DistanceTravelledX[n]
                TotalTravelledTotal += DistanceTravelledTotal[n]
        Results.append([type.Name,nType,TotalTravelledX,TotalTravelledTotal])
    #print(*Results,sep='\n')

    for item in Results:
        print("Type:", item[0], "Average Speed X:", (item[2]/item[1])/(SimulationVariables.TickNumber*SimulationVariables.TickLength),"Average Speed Total:",(item[3]/item[1])/(SimulationVariables.TickNumber*SimulationVariables.TickLength))

#########################################Simulation#########################################
def Simulate():

    # 1: Initialises list of all cells by creating cells of each cell type defined in CellVariables.py
    Cells = InitialiseCells()
    RecordedPositions=[]

    # 2: Initialises plot for animation (if required)
    # If running in real time or replay, sets up plot for animations
    if SimulationVariables.SimulationType == "RealTime" or SimulationVariables.SimulationType == "Replay":
        figure, axes = InitialisePlot()
        InitialiseLegend(axes)
        InitialiseScalebar(axes, figure)
        timer = axes.annotate("0s", xy=(20, 21), xytext=(40,20),horizontalalignment='right',color = 'black')
        # 3: Draws cells (if required)
        for cell in Cells:
            axes.add_artist(cell.Draw())
        plt.ion()

    # 4: Carries out simulation for number of ticks defined in SimulationVariables.py
    # If running in real time, runs simulation, animates and saves position of each cell at each tick
    if SimulationVariables.SimulationType == "RealTime":
        for tick in range(SimulationVariables.TickNumber):
            timer.set_text(str(tick*SimulationVariables.TickLength) + "s")
            # update network of neighbouring cells
            Cells.GenerateNodeNetwork(1)

            for n, cell in enumerate(Cells):
                # update forces acting on cells and velocities defined by those forces
                if cell.Dynamics.Dynamic == True:
                    Cells = CellDynamics.UpdateForces(Cells, n)
            NewPosition = []
            for cell in Cells:
                if cell.Dynamics.Dynamic == True:
                    # 6: Moves cell to new position (once forces/acceleration/velocity have been calculated for ALL cells in current position)
                    cell.UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
                    # 7: Updates actor positions (if required)
                    cell.UpdateArtist()      
                # 8: For each cell, gets its new position and adds it to record of positions of each cell for each tick         
                NewPosition.append([cell.Position.X,cell.Position.Y])
            RecordedPositions.append(NewPosition)
            plt.pause(0.025)

    # 4: Carries out simulation for number of ticks defined in SimulationVariables.py
    # If running as a replay, runs the simulation through and saves position of each cell at each tick, then draws animation based on saved data.
    elif SimulationVariables.SimulationType == "Replay":
        for tick in range(SimulationVariables.TickNumber):
            Cells.GenerateNodeNetwork(1)

            for n, cell in enumerate(Cells):
                # update forces acting on cells and velocities defined by those forces
                if cell.Dynamics.Dynamic == True:
                    Cells = CellDynamics.UpdateForces(Cells, n)
                    # for each cell, updates position due to calculated velocity and appends cell artist information or positions as required
                    # due to simulation types. Updating position is a separate loop to allow all cell velocities to update changing positions.
            
            NewPosition = []
            for cell in Cells:
                if cell.Dynamics.Dynamic == True:
                    cell.UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
                NewPosition.append([cell.Position.X,cell.Position.Y])
            RecordedPositions.append(NewPosition)
        
        for tick, position in enumerate(RecordedPositions):
            timer.set_text(str(tick*SimulationVariables.TickLength)+"s")
            for n, cell in enumerate(position):
                # 6: Moves cell to new position (once forces/acceleration/velocity have been calculated for ALL cells in current position)
                Cells[n].SetPosition(position[n][0],position[n][1])
                # 7: Updates actor positions (if required)
                Cells[n].UpdateArtist()
            plt.pause(0.025)

    # If reporting data only, runs simulation and saves positin of each cell at each tick
    elif SimulationVariables.SimulationType == "Report":
        for tick in range(SimulationVariables.TickNumber):
            # update network of neighbouring cells
            Cells.GenerateNodeNetwork(1)

            for n, cell in enumerate(Cells):
                # update forces acting on cells and velocities defined by those forces
                if cell.Dynamics.Dynamic == True:
                    Cells = CellDynamics.UpdateForces(Cells, n)
            
            NewPosition = []    
            for cell in Cells:
                if cell.Dynamics.Dynamic == True:
                    cell.UpdatePosition(cell.Dynamics.Velocity.X,cell.Dynamics.Velocity.Y)
                NewPosition.append([cell.Position.X,cell.Position.Y])

            RecordedPositions.append(NewPosition)

    #calculate results from RecordedPositions and starting positions
    Results(Cells, RecordedPositions)

    if SimulationVariables.SimulationType == "RealTime" or SimulationVariables.SimulationType == "Replay":
        plt.close()