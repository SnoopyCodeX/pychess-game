import os

PAWN: int = -10
KNIGHT: int = -20
BISHOP: int = -30
ROOK: int = -40
QUEEN: int = -50
KING: int = -60

class Piece:
    
    def __init__(self, name, color, type, original_position=dict, texture = None, texture_rect = None):
        self.name = name
        self.color = color
        self.type = type
        
        self.original_position = original_position
        self.current_position: dict|None = None
        self.valid_moves = []
        self.moved = False
        
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect
        
    def __hash__(self) -> int:
        return hash((self.name, self.color, self.type))
        
    def set_texture(self, size = 80):
        self.texture = os.path.join(
            f'assets/images/imgs-{size}px/{self.color}_{self.name}.png'
        )
        
    def add_valid_move(self, move):
        self.valid_moves.append(move)
        
    def clear_valid_moves(self):
        self.valid_moves = []
        
    def remove_last_move(self):
        if len(self.valid_moves) > 0:
            self.valid_moves.pop()

class Pawn(Piece):
    
    def __init__(self, color, original_position=dict):
        self.type = PAWN
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False
        self.en_passant_capture_location = dict()
        super().__init__('pawn', color, PAWN, original_position=original_position)
        
class Knight(Piece):
    
    def __init__(self, color, original_position=dict):
        self.type = KNIGHT
        super().__init__('knight', color, KNIGHT, original_position=original_position)
        
class Bishop(Piece):
    
    def __init__(self, color, original_position=dict):
        self.type = BISHOP
        super().__init__('bishop', color, BISHOP, original_position=original_position)
        
class Rook(Piece):
    
    def __init__(self, color, original_position=dict):
        self.type = ROOK
        super().__init__('rook', color, ROOK, original_position=original_position)
        
class Queen(Piece):
    
    def __init__(self, color, original_position=dict):
        self.type = QUEEN
        super().__init__('queen', color, QUEEN, original_position=original_position)
        
class King(Piece):
    
    def __init__(self, color, original_position=dict):
        self.left_rook: Rook | None = None
        self.right_rook: Rook | None = None
        self.type = KING
        super().__init__('king', color, KING, original_position=original_position)
    