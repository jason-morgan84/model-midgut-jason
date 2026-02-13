import math
import numpy as np
import main

def Drag(VelocityX, VelocityY):

    VelocityMagnitude = math.hypot(VelocityY, VelocityX)

    if VelocityMagnitude > main.SpeedLimit:
        SpeedLimitForceMagnitude = VelocityMagnitude - main.SpeedLimit
        VelocityUnitVectorX = VelocityX/VelocityMagnitude
        VelocityUnitVectorY = VelocityY/VelocityMagnitude
        SpeedLimitForceX = -VelocityUnitVectorX * SpeedLimitForceMagnitude
        SpeedLimitForceY = -VelocityUnitVectorY * SpeedLimitForceMagnitude
    else:
        SpeedLimitForceX = 0
        SpeedLimitForceY = 0

    return SpeedLimitForceX, SpeedLimitForceY

def Proximity(Cell1Position, Cell2Position, Cell1Radius, Cell2Radius):
    # Repulsive forces due to proximity
    # If the distane between the cells is less than the minimum gap, increase repulsive force in opposite direction
    # Once the gap is less than MinimumDesiredGap, the repulsive force increases gradually from 0 in a parabola
    # centred on MinimumDesiredGap, reaching 1 when Gap is 0 and continuing to increase as any overlap increases

    Distance = math.hypot(Cell2Position.Y - Cell1Position.Y, Cell2Position.X - Cell1Position.X)
    Gap = Distance - Cell1Radius - Cell2Radius

    if Gap < main.MinimumDesiredGap:
        ProximityForceMagnitude = (((1/main.MinimumDesiredGap) ** 2) * (Gap - 1) ** 2) * main.ProximityForce
        DirectionUnitVectorX = (Cell2Position.X - Cell1Position.X) / Distance
        DirectionUnitVectorY = (Cell2Position.Y - Cell1Position.Y) / Distance
        ProximityForceX = -DirectionUnitVectorX * ProximityForceMagnitude
        ProximityForceY = -DirectionUnitVectorY * ProximityForceMagnitude
    else:
        ProximityForceX = 0
        ProximityForceY = 0
    
    return ProximityForceX, ProximityForceY

def Adhesion(Cell1Position, Cell2Position, Cell1Radius, Cell2Radius):

    # Attractive forces due to adhesion
    
    # AdhesionDistance defines desired separation distance of two stably adhered cells.
    # Below AdhesionDistance, no adhesive force is felt.
    # AdhesionForceDistance defines the maximum distance at which an attractive force is felt.
    # Above AdhesionForceDistance, no attractive force is felt.
    # At AdhesionForceDistance, a maximum attractive force is felt.
    # This maximum attractive force is defined by AdhesionForce.
    # As the gap between the cells decreases from AdhesionForceDistance to AdhesionDistance, attractive force decreases to 0
    # According to the formula Force = AdhesionForce * (Gap/AdhesionForceDistance)^3

    Distance = math.hypot(Cell2Position.Y - Cell1Position.Y, Cell2Position.X - Cell1Position.X)
    Gap = Distance - Cell1Radius - Cell2Radius

    if Gap <= main.AdhesionForceDistance:
        if Gap >= main.AdhesionDistance:
            AdhesionForceMagnitude = ((Gap/(main.AdhesionForceDistance)) ** 3) * main.AdhesionForce
        elif Gap < main.AdhesionDistance:
            AdhesionForceMagnitude = 0

        DirectionUnitVectorX = (Cell2Position.X - Cell1Position.X) / Distance
        DirectionUnitVectorY = (Cell2Position.Y - Cell1Position.Y) / Distance

        AdhesionForceX = DirectionUnitVectorX * AdhesionForceMagnitude
        AdhesionForceY = DirectionUnitVectorY * AdhesionForceMagnitude
    else:
        AdhesionForceX = 0
        AdhesionForceY = 0
    
    return AdhesionForceX, AdhesionForceY

def Signalling(Cell1Type, Cell2Type, Cell1Position, Cell2Position):
# Forces due to signalling from VM
# Checks if cell is a PMEC adjacent to (within adhesion distance) of VM. If it is, sets VMAdjacent to true
# If VMAdjacent is true and cell velocity is lower than migration speed, force in the x direction is increased   

    AdjacentCellType = set()    
    if Cell1Type == "PMEC" and Cell2Type == "VM":
        #Distance = math.hypot(NeighbourPositionY - PositionY, NeighbourPositionX - PositionX)
        AdjacentCellType.add(Cell2Type)

def IntrinsicForces(InternalForceVector):
    # Cell intrinsic forces
    # If maximum internal force (InternalForce) is not 0 and there is no internal force on the cell
    # A random force (between 0 and InternalForce) is applied to the cell in a random direction.
    # If the cell is already experiencing an InternalForce, a new direction and random magnitude is chosen
    # The direction is constrained by directionality:
    # If directionality is 1, the force will be in the same direction.
    # If directionality is 0, the force will be in a random direction.
    # If directionality is 0.5, the force will be within 90 degrees of the current force direction.

    if InternalForceVector.X == 0 and InternalForceVector.Y == 0 and main.InternalForceMultiplier != 0:
        InternalForceDirection = np.random.random() * 2 * math.pi
        InternalForceMagnitude = np.random.random() * main.InternalForceMultiplier
    elif main.InternalForceMultiplier != 0:
        InternalForceDirection = math.atan2(InternalForceVector.X,InternalForceVector.Y)
        InternalForceDirection += (np.random.random() - 0.5 ) * 2 * math.pi * (1 - main.Directionality)
        InternalForceMagnitude = np.random.random() * main.InternalForceMultiplier
    else:
        InternalForceMagnitude = 0
        InternalForceDirection = 0

    InternalForceX = InternalForceMagnitude * math.cos(InternalForceDirection)
    InternalForceY = InternalForceMagnitude * math.sin(InternalForceDirection)

    return InternalForceX, InternalForceY

def UpdateForces(Cells):
    for cell in Cells:

        if cell.Type != "VM":

            #Get cell properties for force calculations
            CellRadius = cell.Morphology.Radius
            CellVelocityX = cell.Dynamics.Velocity.X
            CellVelocityY = cell.Dynamics.Velocity.Y
            CellPosition = cell.Position

            #Set-up force variables
            ProximityForceX, ProximityForceY = 0, 0
            AdhesionForceX, AdhesionForceY = 0, 0
            MigrationForceX = 0

            #loop through each neighbouring cell
            for neighbour in cell.Neighbours:

                #get neighbour cell properties for force calculations
                NeighbourPosition = Cells[neighbour].Position
                NeighbourRadius = Cells[neighbour].Morphology.Radius

                #get forces due to proximity from each neighbour and increment
                NewProximityForceX, NewProximityForceY = Proximity(CellPosition, NeighbourPosition, CellRadius, NeighbourRadius)
                ProximityForceX += NewProximityForceX
                ProximityForceY += NewProximityForceY
                
                #get forces due to adhesions from each neighbour and increment
                NewAdhesionForceX, NewAdhesionForceY = Adhesion(CellPosition, NeighbourPosition, CellRadius, NeighbourRadius)
                AdhesionForceX += NewAdhesionForceX
                AdhesionForceY += NewAdhesionForceY

                #get list of neighbouring cell types to define forces due to signalling from neighbours
                AdjacentCellType = Signalling(cell.Type, Cells[neighbour].Type, CellPosition, NeighbourPosition)

            #get drag forces due to excessive speed
            SpeedLimitForceX, SpeedLimitForceY = Drag(CellVelocityX, CellVelocityY)

            #get forces from cell intrinsic activities
            InternalForceX, InternalForceY = IntrinsicForces(cell.Dynamics.InternalForce)
            
            #update forces due to neighbouring cell types
            for item in AdjacentCellType or []:
                if item == "VM":
                    if VelocityX < main.MigrationSpeed:
                        MigrationForceX = main.MigrationForce   

            #sum x and y force components
            TotalForceX = SpeedLimitForceX + ProximityForceX + MigrationForceX + AdhesionForceX + InternalForceX
            TotalForceY = SpeedLimitForceY + ProximityForceY + AdhesionForceY + InternalForceY

            #calcuate acceleration components proportional to radius squared (assumes equal cell densities)
            AccelerationX = TotalForceX/(CellRadius**2)
            AccelerationY = TotalForceY/(CellRadius**2)

            #increments cell velocity components based on acceleration and TickLength (in us)
            VelocityX += AccelerationX * main.TickLength 
            VelocityY += AccelerationY * main.TickLength 

            #sets new values of velocity components for each cell
            cell.Dynamics.Velocity.X = VelocityX
            cell.Dynamics.Velocity.Y = VelocityY

            #sets new cell internal forces
            cell.Dynamics.InternalForce.X = InternalForceX
            cell.Dynamics.InternalForce.Y = InternalForceY

    return Cells
    