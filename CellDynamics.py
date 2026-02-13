import math
import numpy as np

def Drag(VelocityX, VelocityY, SpeedLimit):

    VelocityMagnitude = math.hypot(VelocityY, VelocityX)

    if VelocityMagnitude > SpeedLimit:
        SpeedLimitForceMagnitude = VelocityMagnitude - SpeedLimit
        VelocityUnitVectorX = VelocityX/VelocityMagnitude
        VelocityUnitVectorY = VelocityY/VelocityMagnitude
        SpeedLimitForceX = -VelocityUnitVectorX * SpeedLimitForceMagnitude
        SpeedLimitForceY = -VelocityUnitVectorY * SpeedLimitForceMagnitude
    else:
        SpeedLimitForceX = 0
        SpeedLimitForceY = 0

    return SpeedLimitForceX, SpeedLimitForceY

def Proximity(MinimumDesiredGap, ProximityForce, Cell1Position, Cell2Position, Cell1Radius, Cell2Radius):

    # Repulsive forces due to proximity
    # If the distane between the cells is less than the minimum gap, increase repulsive force in opposite direction
    # Once the gap is less than MinimumDesiredGap, the repulsive force increases gradually from 0 in a parabola
    # centred on MinimumDesiredGap, reaching 1 when Gap is 0 and continuing to increase as any overlap increases

    Distance = math.hypot(Cell2Position.Y - Cell1Position.Y, Cell2Position.X - Cell1Position.X)
    Gap = Distance - Cell1Radius - Cell2Radius

    if Gap < MinimumDesiredGap:
        ProximityForceMagnitude = (((1/MinimumDesiredGap) ** 2) * (Gap - 1) ** 2) * ProximityForce
        DirectionUnitVectorX = (Cell2Position.X - Cell1Position.X) / Distance
        DirectionUnitVectorY = (Cell2Position.Y - Cell1Position.Y) / Distance
        ProximityForceX = -DirectionUnitVectorX * ProximityForceMagnitude
        ProximityForceY = -DirectionUnitVectorY * ProximityForceMagnitude
    else:
        ProximityForceX = 0
        ProximityForceY = 0
    
    return ProximityForceX, ProximityForceY

def Adhesion(AdhesionDistance, AdhesionForceDistance, AdhesionForce, Cell1Position, Cell2Position, Cell1Radius, Cell2Radius):

    # Attractive forces due to adhesion
    # These are felt as soon as AdhesionForceDistance is reached. Attractive forces are at a maximum at 
    # AdhesionForceDistance, decrease to 0 as Gap approaches AdhesionDistance and are 0 below AdhesionDistance.

    Distance = math.hypot(Cell2Position.Y - Cell1Position.Y, Cell2Position.X - Cell1Position.X)
    Gap = Distance - Cell1Radius - Cell2Radius

    if Gap <= AdhesionForceDistance:
        if Gap >= AdhesionDistance:
            AdhesionForceMagnitude = ((Gap/(AdhesionForceDistance)) ** 3) * AdhesionForce
        elif Gap < AdhesionDistance:
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

def IntrinsicForces(InternalForceVector, InternalForceMultiplier, Directionality):
    # Cell intrinsic forces
    # If maximum internal force (InternalForce) is not 0 and there is no internal force on the cell
    # A random force (between 0 and InternalForce) is applied to the cell in a random direction.
    # If the cell is already experiencing an InternalForce, a new direction and random magnitude is chosen
    # The direction is constrained by directionality:
    # If directionality is 1, the force will be in the same direction.
    # If directionality is 0, the force will be in a random direction.
    # If directionality is 0.5, the force will be within 90 degrees of the current force direction.

    if InternalForceVector.X == 0 and InternalForceVector.Y == 0 and InternalForceMultiplier != 0:
        InternalForceDirection = np.random.random() * 2 * math.pi
        InternalForceMagnitude = np.random.random() * InternalForceMultiplier
    elif InternalForceMultiplier != 0:
        InternalForceDirection = math.atan2(InternalForceVector.X,InternalForceVector.Y)
        InternalForceDirection += (np.random.random() - 0.5 ) * 2 * math.pi * (1 - Directionality)
        InternalForceMagnitude = np.random.random() * InternalForceMultiplier
    else:
        InternalForceMagnitude = 0
        InternalForceDirection = 0

    InternalForceX = InternalForceMagnitude * math.cos(InternalForceDirection)
    InternalForceY = InternalForceMagnitude * math.sin(InternalForceDirection)

    return InternalForceX, InternalForceY