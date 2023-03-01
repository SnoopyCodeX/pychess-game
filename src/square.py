from piece import Piece

class Square:
    
    ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    
    def __init__(self, row, col, piece: Piece | None = None):
        self.row = row
        self.col = col
        self.piece = piece
        self.alphacols = self.ALPHACOLS[col]
        
    def __eq__(self, other: object) -> bool:
        return self.row == other.row and self.col == other.col
    
    def __hash__(self) -> int:
        return hash((self.row, self.col, self.piece))
        
    def has_piece(self):
        return self.piece != None
    
    def isempty(self):
        return not self.has_piece()
    
    def has_enemy_piece(self, color):
        return self.has_piece() and self.piece.color != color
    
    def has_team_piece(self, color):
        return self.has_piece() and self.piece.color == color
    
    def isempty_or_enemy(self, color):
        return self.isempty() or self.has_enemy_piece(color)
    
    @staticmethod
    def in_range(*kwargs):
        for arg in kwargs:
            if arg < 0 or arg > 7:
                return False
            
        return True
    
    @staticmethod
    def get_alphacol(col):
        ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        return ALPHACOLS[col] 