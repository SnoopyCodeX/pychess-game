import pygame

from const import *
from piece import Piece

class Dragger:
    
    def __init__(self):
        self.piece: Piece | None = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0
        
        
    def update_blit(self, screen: pygame.Surface, chess_board: pygame.Surface):
        self.piece.set_texture(size = 128)
        img = pygame.image.load(self.piece.texture)
        
        self.piece.texture_rect = img.get_rect(center = (self.mouseX, self.mouseY))
        chess_board.blit(img, self.piece.texture_rect)
        screen.blit(chess_board, (0, 0), chess_board.get_rect(width=WIDTH, height=HEIGHT))
        
    
    def update_mouse(self, position):
        self.mouseX, self.mouseY = position
    
    def save_initial(self, position):
        self.initial_row = position[1] // SQSIZE
        self.initial_col = position[0] // SQSIZE
        
    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True
        
    def undrag_piece(self):
        self.piece = None
        self.dragging = False