import pygame
from config import Config
from const import *
from piece import Piece
from board import Board
from dragger import Dragger
from square import Square

class Game:
    
    def __init__(self):
        self.next_player = 'white'
        self.ai_enemy_enabled = False
        self.ai_turn = False
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
    
    def show_bg(self, screen: pygame.Surface, chess_board: pygame.Surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                    
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(chess_board, color, rect)
                
                # Show numbers on the left side of the board
                if col == 0:
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    label = self.config.font.render(str(ROWS-row), 1, color)
                    label_pos = (5, 5 + row * SQSIZE)
                    chess_board.blit(label, label_pos)
                 
                # Show letters A-H on the bottom of the board   
                if row == 7:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    label = self.config.font.render(Square.get_alphacol(col).upper(), 1, color)
                    label_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    chess_board.blit(label, label_pos)
                    
        screen.blit(chess_board, (0, 0), chess_board.get_rect(width=WIDTH, height=HEIGHT))
    
    def show_pieces(self, screen: pygame.Surface, chess_board: pygame.Surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece: Piece = self.board.squares[row][col].piece
                    
                    if piece is not self.dragger.piece:
                        piece.set_texture()
                        
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        chess_board.blit(img, piece.texture_rect)
                        
        screen.blit(chess_board, (0, 0), chess_board.get_rect(width=WIDTH, height=HEIGHT))
    
    def show_moves(self, screen: pygame.Surface, chess_board: pygame.Surface, current_square: Square|None = None):
        theme = self.config.theme
        
        if self.dragger.dragging:
            piece = self.dragger.piece
            
            if current_square:
                _color = theme.trace.dark
                _rect = (current_square.col * SQSIZE, current_square.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(chess_board, _color, _rect)
            
            for move in piece.valid_moves:
                color = theme.valid_moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.valid_moves.dark
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(chess_board, color, rect)
                
        screen.blit(chess_board, (0, 0), chess_board.get_rect(width=WIDTH, height=HEIGHT))
                
    def show_last_move(self, screen: pygame.Surface, chess_board: pygame.Surface):
        theme = self.config.theme
        
        if self.board.last_move != None:
            initial = self.board.last_move.initial
            final = self.board.last_move.final
            
            for pos in [initial, final]:
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(chess_board, color, rect)
                
        screen.blit(chess_board, (0, 0), chess_board.get_rect(width=WIDTH, height=HEIGHT))
                
    def show_hover(self, screen: pygame.Surface, chess_board: pygame.Surface):
        if self.hovered_sqr:
            color = (180, 180, 180)
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(chess_board, color, rect, width=3)
            
        screen.blit(chess_board, (0, 0), chess_board.get_rect(width=WIDTH, height=HEIGHT))
    
    def enable_ai_enemy(self):
        self.ai_enemy_enabled = not self.ai_enemy_enabled        
    
    def get_state(self):
        return self.board.state        
    
    def undo_last_move(self):
        self.board.undo_last_move()
        
    def can_undo_last_move(self):
        return len(self.board.last_moves) > 0 
                
    def next_turn(self):
        self.ai_turn = not self.ai_turn if self.ai_enemy_enabled else False
        self.next_player = 'white' if self.next_player == 'black' else 'black'
        
    def set_hover(self, row, col):
        if row < 0: row = 0
        elif row > 7: row = 7
        
        if col < 0: col = 0
        elif col > 7: 
            self.hovered_sqr = None
            return
        
        self.hovered_sqr = self.board.squares[row][col]
        
    def change_theme(self):
        self.config.change_theme()
        
    def play_sound(self, captured = False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()
            
    def reset(self):
        self.__init__()