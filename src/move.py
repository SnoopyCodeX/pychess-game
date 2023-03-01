from square import Square

class Move:
    
    def __init__(self, initial: Square, final: Square):
        self.initial: Square = initial
        self.final: Square = final
        
    def __eq__(self, other: object) -> bool:
        if other == None:
            return False
        
        return self.initial == other.initial and self.final == other.final
    
    def __repr__(self) -> str:
        return f'([{self.initial.row}, {self.initial.col}], [{self.final.row}, {self.final.col}])'
    