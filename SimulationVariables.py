#######################################Key Simulation Variables#######################################
PlotWidth = 40                  #   Width of simulation in plot units
Scale = 1                       #   Size of 1 plot unit in um
TickLength = 1                  #   Length of simulation tick in seconds
TickNumber = 1000               #   Length of simulation in ticks
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
MinimumDesiredGap = 0.05        #   Minimum desired gap between cells (gaps can be smaller than this, but repulsive force will increase)
ProximityForce = 0.00005        #   Maximum repulsive force on cells

# Variables for cell intrinsic forces (the force a cell applies to itself to go where it 'wants' to go)
InternalForce = 0.005           #   Maximum force a cell can apply to itself
Directionality = 0              #   Tendency of a cell to maintain a specific direction (1 - straight line, 0 - random direction)

#Variables that define  simulation end point
EndPointX = 0.75                 #   Defines 'finish line' in terms of width of simulation
FinishProportion = 0.5          #   Proportion of cells to have passed EndPointX for simulation to be considered over