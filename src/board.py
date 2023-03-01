import copy
import os
import state
from typing import Type
from const import *
from piece import *
from sound import Sound
from square import Square
from move import Move

class Board:
    
    def __init__(self):
        self.squares: list[list[Type[Square]]] = [[Square, Square, Square, Square, Square, Square, Square, Square] for _ in range(COLS)]
        self.state: int = state.STATE_INITIAL
        self.last_move: Move | None = None
        self.current_player = 'white'
        
        self.winner = ''
        self.score = 0
        
        self.positions: list[str] = []
        self.last_moves: list[dict] = []
        self.move_counter: int = 0
        
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        
        print(f"Initial State: {self.generate_fen()}")
        coords = [(move // 8, move % 8) for move in list(self.get_legal_moves())]
        print(coords)
        
    '''
    Generates FEN string of the board's
    current state
    
    @return str
    '''
    def generate_fen(self):
        fen = ""
        
        for row in range(ROWS):
            for col in range(COLS):
                square: Square = self.squares[row][col]
                
                if square.has_piece():
                    piece: Piece = square.piece
                    
                    if isinstance(piece, Pawn):
                        fen += "p" if piece.color == 'black' else 'P'
                    elif isinstance(piece, Knight):
                        fen += "n" if piece.color == 'black' else 'N'
                    elif isinstance(piece, Bishop):
                        fen += "b" if piece.color == 'black' else 'B'
                    elif isinstance(piece, Rook):
                        fen += "r" if piece.color == 'black' else 'R'
                    elif isinstance(piece, Queen):
                        fen += "q" if piece.color == 'black' else 'Q'
                    elif isinstance(piece, King):
                        fen += "k" if piece.color == 'black' else 'K'
                        
                else:
                    if len(fen) == 0:
                        fen += '1'
                    else:
                        last_char = fen[-1]
                        fen = fen.removesuffix(last_char) if last_char != "/" and last_char.isdigit() else fen
                        fen += str(int(last_char) + 1) if last_char.isdigit() else '1'
            fen += "/"
        
        # Remove extra "/" at the end of the generated FEN string
        fen = fen.removesuffix("/")
        return fen
    
    """Returns a dictionary mapping each square on the board to the piece
    currently occupying that square.
    """
    def get_board_pieces(self):
        pieces = {}
        
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                piece = square.piece
                
                if square.has_piece():
                    pieces[(row * 8 + col)] = piece
                
        return pieces
    
    """Returns a set of pieces"""
    def pieces(self, piece_type, color):
        squares = set()
        
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                
                if square.has_piece() and square.piece.color == color and (square.piece.type == piece_type):
                    squares.add(square)
        
        return squares
    
    def square_mirror(self, square):
        file = square % 8
        rank = square // 8
        
        return (7 - file) + (rank * 8)
    
    def get_legal_moves(self, color = None):
        temp_board = copy.deepcopy(self)
        legal_moves = {}

        for row in range(ROWS):
            for col in range(COLS):
                square: Square = self.squares[row][col]
                
                if square.has_team_piece(self.current_player if color == None else color):
                    piece: Piece = square.piece 
                    temp_board.calc_moves(piece, row, col)
                    
                    if len(piece.valid_moves) > 0:
                        legal_moves[row * 8 + col] = piece
                    
        return legal_moves
    
    def is_capture_move(self, move: Move, color: str):
        return self.squares[move.final.row][move.final.col].has_enemy_piece(color) 
    
    def king(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                
                if square.has_piece() and isinstance(square.piece, King) and square.piece.color == color:
                    return row * 8 + col
                
        return None
    
    def is_game_over(self):
        if self.is_checkmate(color='white') or self.is_checkmate(color='black'):
            return True
        
        if self.is_stalemate(color='white') or self.is_stalemate(color='black'):
            return True
        
        if self.is_insufficient_material():
            return True
        
        if self.state == state.STATE_TF_DRAW:
            return True
        
        if self.state == state.STATE_FM_DRAW:
            return True
        
        return False
    
    '''
    Counts all remaining
    pieces of a specific color
    
    @return dict
    '''
    def count_all_pieces(self, color):
        pieces = {}
        
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_team_piece(color):
                    piece = self.squares[row][col].piece
                    
                    if isinstance(piece, Pawn):
                        count = pieces.get("P", 0)
                        pieces["P"] = count + 1
                        
                    elif isinstance(piece, Knight):
                        count = pieces.get("N", 0)
                        pieces["N"] = count + 1
                        
                    elif isinstance(piece, Bishop):
                        count = pieces.get("B", 0)
                        pieces["B"] = count + 1
                        
                    elif isinstance(piece, Rook):
                        count = pieces.get("R", 0)
                        pieces["R"] = count + 1
                        
                    elif isinstance(piece, Queen):
                        count = pieces.get("Q", 0)
                        pieces["Q"] = count + 1
                        
                    elif isinstance(piece, King):
                        count = pieces.get("K", 0)
                        pieces["K"] = count + 1
        
        return pieces
        
    '''
    Undo last move played
    on the board
    
    @return None
    '''
    def undo_last_move(self):
        # Set the recent move as the current last_move
        if len(self.last_moves) > 0:
            # If the move_counter is greater than 0, decrement 1
            if self.move_counter > 0:
                self.move_counter -= 1
                
            # If positions has entries, pop the most recent position
            if len(self.positions) > 0:
                self.positions.pop()
            
            recent_move = self.last_moves.pop()
            
            is_castling: bool = recent_move.get('castling', False)
            is_en_passant: bool = recent_move.get('en_passant', False)
            captured_piece: Piece | None = recent_move.get('captured_piece', None)
            is_capture_move: bool = recent_move.get('is_capture_move', False)
            
            last_move: Move = recent_move.get('move')
            last_piece: Piece = recent_move.get('piece')
            
            last_piece_row = last_piece.original_position.get('row')
            last_piece_col = last_piece.original_position.get('col')
            
            # If the previous move has captured a piece, return the captured piece to the board
            if is_capture_move:
                # If the previous move was an en passant move, return its captured piece to the board
                if is_en_passant:
                    self.squares[last_move.initial.row][last_move.initial.col].piece = None
                    self.squares[captured_piece.en_passant_capture_location.get('row')][captured_piece.en_passant_capture_location.get('col')].piece = captured_piece
                else:
                    self.squares[last_move.initial.row][last_move.initial.col].piece = captured_piece
            
            # If the previous location of the piece was its original location, reset its "moved" state to False
            if last_piece_row == last_move.final.row and last_piece_col == last_move.final.col:
                last_piece.moved = False
            
            # If the previous move was a castling move, recursively call @self.undo_last_move()
            # because castling has 2 moves, First is the king, next is the rook  
            if is_castling:
                self.undo_last_move()
            
            self.move(last_piece, last_move, revertMove=True, capture_move=is_capture_move)
            self.last_move = self.last_moves[-1].get('move') if len(self.last_moves) > 0 else None
        else:
            print('No saved moves to undo')
        
    def move(self, piece: Piece, move: Move, revertMove=False, capture_move=False, testing=False):
        # Check if the pieces are not insufficient
        if not testing and not revertMove:
            # If pieces are insufficient, do not make a move
            if self.is_insufficient_material():
                print("Insufficient Material, The game is a Draw.")
                return
        
        initial = move.initial
        final = move.final
        
        en_passant_empty = self.squares[final.row][final.col].isempty()
        is_en_passant = False
        
        captured_piece: Piece | None = None
        is_capture_move: bool = False
        
        # If the target square has an enemy piece, save the enemy piece for reverting this move
        if self.squares[final.row][final.col].has_enemy_piece(piece.color):
            self.move_counter = 0 # Reset move counter for 50-move rule
            captured_piece: Piece = self.squares[final.row][final.col].piece
            is_capture_move = True
        
        # Only remove the piece from previous location if it is not a capture_move or we don't want to revertMove
        if not capture_move or not revertMove:
            self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        
        # Pawn Promotion and en passant
        if isinstance(piece, Pawn) and not revertMove:
            # Reset move counter for 50-move rule
            self.move_counter = 0
            
           # en passant capture
            diff = final.col - initial.col
            
            if diff != 0 and en_passant_empty:
                captured_piece: Pawn = self.squares[initial.row][initial.col + diff].piece
                captured_piece.en_passant_capture_location = dict(row=initial.row, col=initial.col + diff)
                is_capture_move = True
                is_en_passant = True
                
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(
                        os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            else:
                self.check_promotion(piece, final)
        
        # King Castling
        if isinstance(piece, King) and not revertMove:
            if self.castling(initial, final):
                diff = final.col - initial.col
                rook = piece.left_rook if diff < 0 else piece.right_rook
                self.move(rook, rook.valid_moves[-1])
        
        # Move Piece
        piece.moved = True if not revertMove else piece.moved
        piece.current_position = dict(row=final.row, col=final.col)
        piece.clear_valid_moves()
        
        # Set last move
        self.last_move = move
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        if not testing and not revertMove:
            # Add current fen position to self.positions
            self.positions.append(self.generate_fen())
        
        # Add piece and move to last_moves array if we're not reverting a move and not testing a move
        if not revertMove and not testing:
            move_history = Move(initial=move.final, final=move.initial)
            self.last_moves.append(dict(
                piece=copy.deepcopy(piece), 
                move=copy.deepcopy(move_history),
                castling=isinstance(piece, King) and self.castling(initial, final) and not (not piece.moved),
                en_passant=is_en_passant,
                captured_piece=copy.deepcopy(captured_piece),
                is_capture_move=is_capture_move
            ))
        
        # Checkmate detection, stalemate detection, 50-move rule, Three-fold repitition draw
        if not testing and not revertMove:
            # If the same positions occured in the board thrice, it is a Three-fold repetition
            if len(self.positions) > 0 and self.positions.count(self.generate_fen()) >= 3:
                print("Three-fold repetition! Game is a draw.")
                self.state = state.STATE_TF_DRAW
                
            # If no capture has been made or no pawn has been moved since the last move, increase the move_counter
            if not is_capture_move and not isinstance(piece, Pawn):
                self.move_counter += 1
                
                # If the move counter reaches 100, it means that both players
                # have made 50 consecutive moves without capture or pawn movement
                if self.move_counter >= 100:
                    print("50 move Draw!")
                    self.state = state.STATE_FM_DRAW
            
            # If enemy is in checkmate
            if self.is_checkmate(piece=piece):
                print("CHECKMATE!")
                
            # If enemy is stalemate
            if self.is_stalemate(piece=piece):
                print("STALEMATE!")
        
    def check_promotion(self, piece: Piece, final: Square):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color, original_position=piece.original_position)
            
    def castling(self, initial: Square, final: Square):
        return abs(initial.col - final.col) == 2
    
    def en_passant(self, initial: Square, final: Square):
        return abs(initial.row - final.row) == 2
    
    def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True
    
    def in_check(self, piece: Piece, move: Move|None):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        
        if move != None:
            temp_board.move(temp_piece, move, testing=True)
        
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    _piece = temp_board.squares[row][col].piece
                    temp_board.calc_moves(_piece, row, col, fromMain = False)
                    
                    for _move in _piece.valid_moves:
                        if isinstance(_move.final.piece, King):
                            return True
                        
        return False
    
    def is_check(self, color = None, piece: Piece|None = None):
        temp_piece: Piece|None = copy.deepcopy(piece) if piece else None
        temp_board = copy.deepcopy(self)
        
        if not piece:
            for row in range(ROWS):
                for col in range(COLS):
                    square = self.squares[row][col]
                    
                    if square.has_enemy_piece(self.current_player if color == None else color):
                        piece: Piece = square.piece
                        temp_board.calc_moves(piece, row, col)
                        
                        for move in piece.valid_moves:
                            if isinstance(move.final.piece, King):
                                return True
        else:
            row = temp_piece.current_position.get("row")
            col = temp_piece.current_position.get("col")
            temp_board.calc_moves(temp_piece, row, col)
            
            for move in temp_piece.valid_moves:
                if isinstance(move.final.piece, King):
                    return True
                        
        return False
    
    def valid_move(self, piece: Piece, move: Move):
        return move in piece.valid_moves
    
    def is_checkmate(self, color = None, piece: Piece = None):
        temp_board: Board = copy.deepcopy(self)
                        
        # If the enemy's king is in check, check if all the enemy's piece (including their king) has valid moves
        if self.is_check(color=color, piece=piece):
            for _row in range(ROWS):
                for _col in range(COLS):
                    if temp_board.squares[_row][_col].has_enemy_piece(self.current_player if color == None else color):
                        enemy_piece: Piece = temp_board.squares[_row][_col].piece
                        temp_board.calc_moves(enemy_piece, _row, _col)
                        
                        # If enemy's piece has valid moves, then enemy is not yet checkmate
                        if len(enemy_piece.valid_moves) > 0:
                            return False
        else:
            return False
                
        return True
    
    def attackers(self, color, target_square):
        temp_board = copy.deepcopy(self)
        target_row = target_square // 8
        target_col = target_square % 8
        attackers = []
        
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                
                if square.has_team_piece(color):
                    piece: Piece = square.piece
                    temp_board.calc_moves(piece, row, col)
                    
                    moves = [(move.final.row, move.final.col) for move in piece.valid_moves]
                    
                    if (target_row, target_col) in moves:
                        attackers.append((piece, (row, col)))
        
        return attackers
    
    def is_stalemate(self, color = None, piece: Piece|None = None):
        temp_board: Board = copy.deepcopy(self)
                        
        # If the enemy's king is not in check, check if all the enemy's piece (including their king) has valid moves
        # that will not put their king in check
        if not self.is_check(color=color, piece=piece):
            for _row in range(ROWS):
                for _col in range(COLS):
                    if temp_board.squares[_row][_col].has_enemy_piece(self.current_player if color == None else color):
                        enemy_piece: Piece = temp_board.squares[_row][_col].piece
                        temp_board.calc_moves(enemy_piece, _row, _col)
                        
                        if len(enemy_piece.valid_moves) > 0:
                            return False
        else:
            return False
                
        return True
    
    def is_insufficient_material(self):
        white_pieces = self.count_all_pieces("white")
        black_pieces = self.count_all_pieces("black")
        
        return (white_pieces == {"K": 1} and black_pieces == {"K": 1}) or \
            (white_pieces == {"K": 1, "B": 1} and black_pieces == {"K": 1}) or \
            (white_pieces == {"K": 1} and black_pieces == {"K": 1, "B": 1}) or \
            (white_pieces == {"K": 1, "N": 1} and black_pieces == {"K": 1}) or \
            (white_pieces == {"K": 1} and black_pieces == {"K": 1, "N": 1}) or \
            (white_pieces == {"K": 1, "B": 1} and black_pieces == {"K": 1, "B": 1}) or \
            (white_pieces == {"K": 1, "N": 1} and black_pieces == {"K": 1, "N": 1})
    
    def calc_moves(self, piece: Piece, row, col, fromMain = True):
        
        def knight_moves():
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]
            
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # Create squares of the move
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        
                        # Create a new move
                        move = Move(initial, final)
                        
                        # Check for potential checks
                        if fromMain:
                            if not self.in_check(piece, move):
                                # Append new move
                                piece.add_valid_move(move)
                            else: continue
                        else:
                            # Append new move
                            piece.add_valid_move(move)
        
        def pawn_moves():
            steps = 1 if piece.moved else 2
            
            # Vertical Moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        # Create squares of the move
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        
                        # Create a new move
                        move = Move(initial, final)
                        
                        # Check for potential checks
                        if fromMain:
                            if not self.in_check(piece, move):
                                # Append new move
                                piece.add_valid_move(move)
                        else:
                            # Append new move
                            piece.add_valid_move(move)
                        
                    else: break
                else: break
            
            # Diagonal Moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # Create squares of the move
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        
                        # Create a new move
                        move = Move(initial, final)
                        
                        # Check for potential checks
                        if fromMain:
                            if not self.in_check(piece, move):
                                # Append new move
                                piece.add_valid_move(move)
                        else:
                            # Append new move
                            piece.add_valid_move(move)
        
            # En Passant Moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            
            # Left En Passant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    __piece = self.squares[row][col-1].piece
                    if isinstance(__piece, Pawn):
                        if __piece.en_passant:
                            # Create squares of the move
                            initial = Square(row, col)
                            final = Square(fr, col-1, __piece)
                            
                            # Create a new move
                            move = Move(initial, final)
                            
                            # Check for potential checks
                            if fromMain:
                                if not self.in_check(piece, move):
                                    # Append new move
                                    piece.add_valid_move(move)
                            else:
                                # Append new move
                                piece.add_valid_move(move)
                                
            # Right En Passant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemy_piece(piece.color):
                    __piece = self.squares[row][col+1].piece
                    if isinstance(__piece, Pawn):
                        if __piece.en_passant:
                            # Create squares of the move
                            initial = Square(row, col)
                            final = Square(fr, col+1, __piece)
                            
                            # Create a new move
                            move = Move(initial, final)
                            
                            # Check for potential checks
                            if fromMain:
                                if not self.in_check(piece, move):
                                    # Append new move
                                    piece.add_valid_move(move)
                            else:
                                # Append new move
                                piece.add_valid_move(move)
        
        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr
                
                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # Create squares of the move
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        
                        # Create new move
                        move = Move(initial, final)
                        
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            # Check for potential checks
                            if fromMain:
                                if not self.in_check(piece, move):
                                    # Append new move
                                    piece.add_valid_move(move)
                            else:
                                # Append new move
                                piece.add_valid_move(move)
                        
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # Check for potential checks
                            if fromMain:
                                if not self.in_check(piece, move):
                                    # Append new move
                                    piece.add_valid_move(move)
                            else:
                                # Append new move
                                piece.add_valid_move(move)
                            break
                        
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                        
                    else: break
                    
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr
        
        def king_moves():
            adjs = [
                (row-1, col+0), # up
                (row-1, col+1), # upper right
                (row+0, col+1), # right
                (row+1, col+1), # bottom right
                (row+1, col+0), # bottom
                (row+1, col-1), # bottom left
                (row+0, col-1), # left
                (row-1, col-1), # upper left
            ]
            
            # Normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move
                
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # Create squares of the move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        
                        # Create new move
                        move = Move(initial, final)
                        
                        # Check for potential checks
                        if fromMain:
                            if not self.in_check(piece, move):
                                # Append new move
                                piece.add_valid_move(move)
                            else: continue
                        else:
                            # Append new move
                            piece.add_valid_move(move)
                        
            # Castling moves
            if not piece.moved:
                # Queen castling
                left_rook = self.squares[row][0].piece
                
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for _col in range(1, 4):
                            if self.squares[row][_col].has_piece():
                                break
                            
                            if _col == 3:
                                # Add left rook to king
                                piece.left_rook = left_rook
                                
                                # Rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)
                                
                                # King move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)
                                
                                # Check for potential checks
                                if fromMain:
                                    # Append new move to Rook
                                    piece.left_rook.add_valid_move(moveR)
                                    
                                    if not self.in_check(piece, moveK) and not self.in_check(piece.left_rook, moveR):
                                        # Append new move to King
                                        piece.add_valid_move(moveK)
                                    else:
                                        piece.left_rook.remove_last_move()
                                        
                                else:
                                    # Append new move to Rook
                                    piece.left_rook.add_valid_move(moveR)
                                    # Append new move to King
                                    piece.add_valid_move(moveK)
                                
                # King castling
                right_rook = self.squares[row][7].piece
                
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for _col in range(5, 7):
                            if self.squares[row][_col].has_piece():
                                break
                            
                            if _col == 6:
                                # Add right rook to king
                                piece.right_rook = right_rook
                                
                                # Rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)
                                
                                # King move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)
                                
                                # Check for potential checks
                                if fromMain:
                                    # Append new move to Rook
                                    piece.right_rook.add_valid_move(moveR)
                                    
                                    if not self.in_check(piece, moveK) and not self.in_check(piece.right_rook, moveR):
                                        # Append new move to King
                                        piece.add_valid_move(moveK)
                                    else:
                                        piece.right_rook.remove_last_move()
                                        
                                else:
                                    # Append new move to Rook
                                    piece.right_rook.add_valid_move(moveR)
                                    # Append new move to King
                                    piece.add_valid_move(moveK)
                                
        
        if isinstance(piece, Pawn): pawn_moves()
        elif isinstance(piece, Knight): knight_moves()
        elif isinstance(piece, Bishop): straightline_moves([
            (-1, 1), # upper right
            (-1, -1), # upper left
            (1, 1), # bottom right
            (1, -1) # bottom left
        ])
        elif isinstance(piece, Rook): straightline_moves([
            (-1, 0), # up
            (0, 1), # right
            (1, 0), # down
            (0, -1) # left
        ])
        elif isinstance(piece, Queen): straightline_moves([
            (-1, 1), # upper right
            (-1, -1), # upper left
            (1, 1), # bottom right
            (1, -1), # bottom left
            (-1, 0), # up
            (0, 1), # right
            (1, 0), # down
            (0, -1) # left
        ])
        elif isinstance(piece, King): king_moves()
    
    def _create(self):
        
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)
    
    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        
        # Pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color, original_position=dict(row=row_pawn, col=col)))
        
        # Knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color, original_position=dict(row=row_other, col=1)))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color, original_position=dict(row=row_other, col=6)))
        
        # Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color, original_position=dict(row=row_other, col=2)))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color, original_position=dict(row=row_other, col=5)))
        
        # Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color, original_position=dict(row=row_other, col=0)))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color, original_position=dict(row=row_other, col=7)))
        
        # Queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color, original_position=dict(row=row_other, col=3)))
        
        # King
        self.squares[row_other][4] = Square(row_other, 4, King(color, original_position=dict(row=row_other, col=4)))
            