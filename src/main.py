import pygame
import sys
from threading import Thread
from piece import Piece
import state
from copy import deepcopy
from board import Board
from const import *
from dragger import Dragger
from game import Game
from move import Move
from square import Square
from ai import AI

# Main Class
class Main:
    
    def __init__(self):
        pygame.init()
        
        self._init_screen()
        self.game = Game()
        self.ai = AI()
        self.clicked_square: Square|None = None
        
    def _init_screen(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.screen.fill(color='#ffffff')
        pygame.display.set_caption("Py-Chess Game")
        
        self.chess_board = pygame.Surface((WIDTH, HEIGHT))
        self.screen.blit(self.chess_board, (0, 0), self.chess_board.get_rect(width=WIDTH, height=HEIGHT))
    
    def ai_thread(thread, ai: AI, board: Board):
        thread.best_move =  ai.find_best_move(deepcopy(board), 3)
    
    def main_game(self, screen: pygame.Surface, chess_board: pygame.Surface, game: Game, ai: AI, board: Board, dragger: Dragger):
        if game.ai_enemy_enabled and game.ai_turn:
            thread = Thread(target=self.ai_thread, args=(ai, game.board))
            thread.start()
            thread.join()
            
            best_move = thread.best_move
            
            if not isinstance(best_move, int):
                piece, move = best_move
                captured = board.squares[move.final.row][move.final.col].has_piece()
                game.board.move(piece, move)
                
                board.set_true_en_passant(dragger.piece)
                game.play_sound(captured)
                game.show_bg(screen, chess_board)
                game.show_last_move(screen, chess_board)
                game.show_pieces(screen, chess_board)
            
            game.next_turn()
        
        game.show_bg(screen, chess_board)
        game.show_last_move(screen, chess_board)
        game.show_moves(screen, chess_board, current_square=self.clicked_square)
        game.show_pieces(screen, chess_board)
        
        game.show_hover(screen, chess_board)
        
        if dragger.dragging:
            dragger.update_blit(screen, chess_board)
        
        for event in pygame.event.get():
            
            # Click Triggered
            if event.type == pygame.MOUSEBUTTONDOWN and not game.ai_turn:
                dragger.update_mouse(event.pos)
                
                clicked_row = dragger.mouseY // SQSIZE
                clicked_col = dragger.mouseX // SQSIZE
                
                if clicked_row > 7: clicked_row = 7
                elif clicked_row < 0: clicked_row = 0
                
                if clicked_col > 7: continue
                elif clicked_col < 0: clicked_col = 0
                
                if board.squares[clicked_row][clicked_col].has_piece():
                    piece = board.squares[clicked_row][clicked_col].piece
                    
                    if piece.color == game.next_player and not game.ai_turn:
                        self.clicked_square = Square(clicked_row, clicked_col)
                        board.calc_moves(piece, clicked_row, clicked_col, fromMain = True)
                        
                        dragger.save_initial(event.pos)
                        dragger.drag_piece(piece)
                        
                        game.show_bg(screen, chess_board)
                        game.show_last_move(screen, chess_board)
                        game.show_moves(screen, chess_board, current_square=self.clicked_square)
                        game.show_pieces(screen, chess_board)
            
            # Mouse Motion
            elif event.type == pygame.MOUSEMOTION:
                motion_row = event.pos[1] // SQSIZE
                motion_col = event.pos[0] // SQSIZE
                
                if motion_row < 0: motion_row = 0
                elif motion_row > 7: motion_row = 7
                
                if motion_col < 0: motion_col = 0
                elif motion_col > 7: continue
                
                game.set_hover(motion_row, motion_col)
                
                if dragger.dragging:
                    dragger.update_mouse(event.pos)
                    
                    game.show_bg(screen, chess_board)
                    game.show_last_move(screen, chess_board)
                    game.show_moves(screen, chess_board, current_square=self.clicked_square)
                    game.show_pieces(screen, chess_board)
                    game.show_hover(screen, chess_board)
                    dragger.update_blit(screen, chess_board)
            
            # Click Released
            elif event.type == pygame.MOUSEBUTTONUP:
                self.clicked_square = None
                
                if dragger.dragging:
                    dragger.update_mouse(event.pos)
                    released_row = dragger.mouseY // SQSIZE
                    released_col = dragger.mouseX // SQSIZE
                    
                    if released_row < 0: released_row = 0
                    elif released_row > 7: released_row = 7
                    
                    if released_col < 0: released_col = 0
                    elif released_col > 7: released_col = 7
                    
                    # Clear last valid moves if the piece hasn't been moved
                    if dragger.initial_row == released_row and dragger.initial_col == released_col:
                        board.squares[released_row][released_col].piece.clear_valid_moves()
                    
                    initial = Square(dragger.initial_row, dragger.initial_col)
                    final = Square(released_row, released_col)
                    move = Move(initial, final)
                    
                    if board.valid_move(dragger.piece, move):
                        captured = board.squares[released_row][released_col].has_piece()
                        
                        board.move(dragger.piece, move)
                        board.set_true_en_passant(dragger.piece)
                        game.play_sound(captured)
                        game.show_bg(screen, chess_board)
                        game.show_last_move(screen, chess_board)
                        game.show_pieces(screen, chess_board)
                        
                        game.next_turn()
                
                dragger.undrag_piece()
            
            # Keypress
            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_t:
                    game.change_theme()
                    
                elif event.key == pygame.K_r:
                    self.mainloop(reset=True)
                    
                elif event.key == pygame.K_m:
                    game.enable_ai_enemy()
                    print(f"AI is {'enabled' if  game.ai_enemy_enabled else 'disabled'}!")
                    
                elif event.key == pygame.K_u:
                    if game.can_undo_last_move():
                        game.undo_last_move()
                        
                        game.play_sound()
                        game.show_bg(screen, chess_board)
                        game.show_last_move(screen, chess_board)
                        game.show_pieces(screen, chess_board)
                        
                        game.next_turn()
                        
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
            # Quit
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    def mainloop(self, reset=False):
        if reset: self.game.reset()
            
        screen = self.screen
        chess_board = self.chess_board
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        ai = self.ai
        
        while True:
            game_state = game.get_state()
            
            if game_state == state.STATE_INITIAL or game_state == state.STATE_PLAYING:
                self.main_game(screen, chess_board, game, ai, board, dragger)
                
            pygame.display.update()

# Create instance of Main class and execute mainloop() function
main = Main()
main.mainloop()