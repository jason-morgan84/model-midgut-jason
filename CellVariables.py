import CellClasses


#Define cell types and starting positions
OverallCellTypes=[]

OverallCellTypes.append(CellClasses.CellTypes(Name = "PMEC", Format = CellClasses.Format(FillColour = 'powderblue'),
                StartingPosition = 
                    [CellClasses.StartingPosition(
                        ID = "UpperPMEC",
                        Position = CellClasses.XY(-41,16),
                        Morphology = CellClasses.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 30),
                    CellClasses.StartingPosition(
                        ID = "LowerPMEC",
                        Position = CellClasses.XY(-41,5),
                        Morphology = CellClasses.Morphology(Radius = 1),
                        Arrange = "XAlign",
                        Number = 30)]))

OverallCellTypes.append(CellClasses.CellTypes(Name = "VM",Format = CellClasses.Format(FillColour = 'plum'),
                StartingPosition = 
                    [CellClasses.StartingPosition(
                        ID = "UpperVM",
                        Position = CellClasses.XY(-41,17.5),
                        Morphology = CellClasses.Morphology(Radius = 0.5),
                        Arrange = "XAlign",
                        Number = 100),
                    CellClasses.StartingPosition(
                        ID = "LowerVM",
                        Position = CellClasses.XY(-41,3.5),
                        Morphology = CellClasses.Morphology(Radius = 0.5),
                        Arrange = "XAlign",
                        Number = 100)]))

OverallCellTypes.append(CellClasses.CellTypes(Name = "Other",Format = CellClasses.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [CellClasses.StartingPosition(
                        ID = "Other",
                        Position = CellClasses.XY(-41,7),
                        Morphology = CellClasses.Morphology(Radius = 1),
                        Arrange = 'Pack',
                        DrawLimits = CellClasses.XY(21,15.67),
                        Density = 1)]))

""" OverallCellTypes.append(Cell.CellTypes(Name = "Other",Format = Cell.Format(FillColour = 'palegreen'),
                StartingPosition = 
                    [Cell.StartingPosition(
                        ID = "Other",
                        Position = Cell.XY(11,7),
                        Morphology = Cell.Morphology(Radius = 1))])) """