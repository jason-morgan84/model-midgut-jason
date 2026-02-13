import Cell


#Define cell types and starting positions
OverallCellTypes=[]

OverallCellTypes.append(Cell.CellTypes(Name = "PMEC", Format = Cell.Format(FillColour = 'powderblue'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperPMEC",
                        Position = Cell.XY(-21,16),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 20),
                    Cell.StartingPosition(
                        ID = "LowerPMEC",
                        Position = Cell.XY(-21,5),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 20)]))

OverallCellTypes.append(Cell.CellTypes(Name = "VM",Format = Cell.Format(FillColour = 'plum'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "UpperVM",
                        Position = Cell.XY(-21,17.5),
                        Morphology = Cell.Morphology(Radius = 0.5),
                        Arrange = "XAlign",
                        Number = 100),
                    Cell.StartingPosition(
                        ID = "LowerVM",
                        Position = Cell.XY(-21,3.5),
                        Morphology = Cell.Morphology(Radius = 0.5),
                        Arrange = "XAlign",
                        Number = 100)]))

OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(-21,7),
                        Morphology = Cell.Morphology(Radius = 1),
                        Arrange = 'Pack',
                        DrawLimits = Cell.XY(21,15.67),
                        Density = 1)]))

""" OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(11,7),
                        Morphology = Cell.Morphology(Radius = 1))])) """