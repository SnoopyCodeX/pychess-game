from board import Board
from piece import *

class AI:
    
    def __init__(self):
        self.MATERIAL_VALUES = {
            PAWN: 100,
            KNIGHT: 320,
            BISHOP: 330,
            ROOK: 500,
            QUEEN: 900,
            KING: 20000
        }
        
        self.PAWN_TABLE = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]

        self.PIECE_VALUES = {
            KNIGHT: 30,
            BISHOP: 30,
            ROOK: 50,
            QUEEN: 90
        }

        self.MOBILITY_BONUS = 5
        self.KING_SAFETY_BONUS = 10
        self.CHECKMATE_SCORE = 10000
        self.STALEMATE_SCORE = 0
    
    def evaluate(self, board: Board):
        material_score = 0
        for piece_type, value in self.MATERIAL_VALUES.items():
            material_score += len(board.pieces(piece_type, 'white')) * value
            material_score -= len(board.pieces(piece_type, 'black')) * value
            
        pawn_score = 0
        for square, piece in board.get_board_pieces().items():
            if piece.type == PAWN:
                if piece.color == 'white':
                    pawn_score += self.PAWN_TABLE[square]
                else:
                    pawn_score -= self.PAWN_TABLE[board.square_mirror(square)]
                    
        mobility_score = 0
        for _, piece in board.get_legal_moves().items():
            for move in piece.valid_moves:
                if board.is_capture_move(move, piece.color):
                    if not isinstance(board.squares[move.final.row][move.final.col].piece, Pawn) and not isinstance(board.squares[move.final.row][move.final.col].piece, King):
                        mobility_score += self.PIECE_VALUES[board.squares[move.final.row][move.final.col].piece.type]
                else:
                    mobility_score += self.MOBILITY_BONUS
                    
        king_square = board.king('white')
        if board.is_checkmate(color='white'):
            king_score = -self.CHECKMATE_SCORE
        elif board.is_stalemate(color='white'):
            king_score = self.STALEMATE_SCORE
        elif board.is_insufficient_material():
            king_score = 0
        else:
            king_score = self.KING_SAFETY_BONUS * len(board.attackers('black', king_square))
            
        score = material_score + pawn_score + mobility_score + king_score
        return score if board.current_player == 'white' else -score
    

    # Implement the minimax algorithm with alpha-beta pruning
    def minimax(self, board: Board, depth, alpha, beta, maximizing_player):
        print(f"Depth: {depth}, Alpha: {alpha}, Beta: {beta}, MaxP: {maximizing_player}")
        
        # Check if the search has reached the maximum depth or a terminal node
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        # Determine the legal moves for the current player
        if maximizing_player:
            legal_moves = board.get_legal_moves()
            best_value = -float("inf")
            
            for _, piece in legal_moves.items():
                print(f'Evaluating {piece.name}@{piece.color} at depth {depth}')
                
                for move in piece.valid_moves:
                    board.move(piece, move)
                    value = self.minimax(board, depth - 1, alpha, beta, False)
                    board.undo_last_move()
                    
                    best_value = max(best_value, value)
                    alpha = max(alpha, best_value)
                    
                    if beta <= alpha:
                        break
                
            return best_value
        else:
            legal_moves = board.get_legal_moves()
            best_value = float("inf")
            
            for _, piece in legal_moves.items():
                print(f'Evaluating {piece.name}@{piece.color} at depth {depth}')
                
                for move in piece.valid_moves:
                    board.move(piece, move)
                    value = self.minimax(board, depth - 1, alpha, beta, True)
                    board.undo_last_move()
                    
                    best_value = min(best_value, value)
                    beta = min(beta, best_value)
                    
                    if beta <= alpha:
                        break
                
            return best_value

    # Find the best move using the minimax algorithm with alpha-beta pruning
    def find_best_move(self, board: Board, depth):
        print("AI is thinking...")
        legal_moves = board.get_legal_moves()
        first_value = next(iter(legal_moves.values()))
        best_move = (first_value, first_value.valid_moves)
        best_value = -float("inf")
        alpha = -float("inf")
        beta = float("inf")
        
        for _, piece in legal_moves.items():
            for move in piece.valid_moves:
                board.move(piece, move)
                value = self.minimax(board, depth - 1, alpha, beta, False)
                board.undo_last_move()
                
                if value > best_value:
                    best_value = value
                    best_move = (piece, move)
                    
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
                
        return best_move
