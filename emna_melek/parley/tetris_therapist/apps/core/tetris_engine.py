"""
Tetris game engine - handles all game logic server-side.
"""
import random
import json


# Tetromino shapes (7 pieces: I, O, T, S, Z, J, L)
TETROMINOES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]],
        [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0]],
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
    ],
    'O': [
        [[1, 1],
         [1, 1]]
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]]
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ]
}

# Colors for each piece
PIECE_COLORS = {
    'I': '#00f0f0',  # Cyan
    'O': '#f0f000',  # Yellow
    'T': '#a000f0',  # Purple
    'S': '#00f000',  # Green
    'Z': '#f00000',  # Red
    'J': '#0000f0',  # Blue
    'L': '#f0a000',  # Orange
}

# Scoring: single, double, triple, tetris
SCORE_VALUES = {
    1: 100,
    2: 300,
    3: 500,
    4: 800
}


class TetrisEngine:
    """Main Tetris game engine."""
    
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    
    def __init__(self, game_state=None):
        """Initialize game engine with optional saved state."""
        if game_state:
            self.board = game_state.get('board', self._create_empty_board())
            self.current_piece = game_state.get('current_piece')
            self.current_x = game_state.get('current_x', 3)
            self.current_y = game_state.get('current_y', 0)
            self.current_rotation = game_state.get('current_rotation', 0)
            self.next_piece_type = game_state.get('next_piece_type', self._get_random_piece())
            self.held_piece = game_state.get('held_piece')
            self.can_hold = game_state.get('can_hold', True)
            self.score = game_state.get('score', 0)
            self.lines_cleared = game_state.get('lines_cleared', 0)
            self.level = game_state.get('level', 1)
            self.game_over = game_state.get('game_over', False)
            self.paused = game_state.get('paused', False)
            self.stats = game_state.get('stats', {
                'total_rotations': 0,
                'hold_uses': 0,
                'hard_drops': 0,
                'soft_drops': 0,
                'tetris_count': 0,
                'total_pieces': 0,
            })
        else:
            self.board = self._create_empty_board()
            self.current_piece = None
            self.current_x = 3
            self.current_y = 0
            self.current_rotation = 0
            self.next_piece_type = self._get_random_piece()
            self.held_piece = None
            self.can_hold = True
            self.score = 0
            self.lines_cleared = 0
            self.level = 1
            self.game_over = False
            self.paused = False
            self.stats = {
                'total_rotations': 0,
                'hold_uses': 0,
                'hard_drops': 0,
                'soft_drops': 0,
                'tetris_count': 0,
                'total_pieces': 0,
            }
            self._spawn_new_piece()
    
    def _create_empty_board(self):
        """Create an empty game board."""
        return [[0 for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
    
    def _get_random_piece(self):
        """Get a random tetromino type."""
        return random.choice(list(TETROMINOES.keys()))
    
    def _spawn_new_piece(self):
        """Spawn a new piece at the top."""
        self.current_piece = self.next_piece_type
        self.next_piece_type = self._get_random_piece()
        self.current_x = 3
        self.current_y = 0
        self.current_rotation = 0
        self.can_hold = True
        self.stats['total_pieces'] += 1
        
        # Check if game is over (piece can't be placed)
        if not self._is_valid_position(self.current_piece, self.current_rotation, self.current_x, self.current_y):
            self.game_over = True
    
    def _get_piece_shape(self, piece_type, rotation):
        """Get the shape of a piece at a specific rotation."""
        shapes = TETROMINOES[piece_type]
        return shapes[rotation % len(shapes)]
    
    def _is_valid_position(self, piece_type, rotation, x, y):
        """Check if a piece can be placed at the given position."""
        shape = self._get_piece_shape(piece_type, rotation)
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    
                    # Check boundaries
                    if board_x < 0 or board_x >= self.BOARD_WIDTH:
                        return False
                    if board_y >= self.BOARD_HEIGHT:
                        return False
                    if board_y < 0:
                        continue
                    
                    # Check collision with existing blocks
                    if self.board[board_y][board_x] != 0:
                        return False
        
        return True
    
    def _place_piece(self, piece_type, rotation, x, y):
        """Place a piece on the board."""
        shape = self._get_piece_shape(piece_type, rotation)
        color = PIECE_COLORS[piece_type]
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    if 0 <= board_y < self.BOARD_HEIGHT and 0 <= board_x < self.BOARD_WIDTH:
                        self.board[board_y][board_x] = color
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.game_over:
            return False
        self.paused = not self.paused
        return True
    
    def move_left(self):
        """Move current piece left."""
        if self.game_over or self.paused:
            return False
        
        new_x = self.current_x - 1
        if self._is_valid_position(self.current_piece, self.current_rotation, new_x, self.current_y):
            self.current_x = new_x
            return True
        return False
    
    def move_right(self):
        """Move current piece right."""
        if self.game_over or self.paused:
            return False
        
        new_x = self.current_x + 1
        if self._is_valid_position(self.current_piece, self.current_rotation, new_x, self.current_y):
            self.current_x = new_x
            return True
        return False
    
    def move_down(self):
        """Move current piece down (soft drop)."""
        if self.game_over or self.paused:
            return False
        
        new_y = self.current_y + 1
        if self._is_valid_position(self.current_piece, self.current_rotation, self.current_x, new_y):
            self.current_y = new_y
            self.stats['soft_drops'] += 1
            return True
        else:
            # Piece has landed
            self._lock_piece()
            return False
    
    def hard_drop(self):
        """Hard drop - instantly drop piece to bottom."""
        if self.game_over or self.paused:
            return False
        
        drop_distance = 0
        while self._is_valid_position(self.current_piece, self.current_rotation, 
                                      self.current_x, self.current_y + 1):
            self.current_y += 1
            drop_distance += 1
        
        self.stats['hard_drops'] += 1
        self.score += drop_distance * 2  # Bonus for hard drop
        self._lock_piece()
        return True
    
    def rotate(self):
        """Rotate current piece clockwise."""
        if self.game_over or self.paused:
            return False
        
        new_rotation = (self.current_rotation + 1) % len(TETROMINOES[self.current_piece])
        
        # Special handling for I-piece (needs better wall kicks)
        if self.current_piece == 'I':
            # I-piece wall kicks: try multiple positions
            kick_offsets = [
                (0, 0),      # Current position
                (-1, 0),     # Left 1
                (1, 0),      # Right 1
                (-2, 0),     # Left 2
                (2, 0),      # Right 2
                (0, -1),     # Up 1
                (-1, -1),    # Up-left
                (1, -1),     # Up-right
            ]
            
            for x_offset, y_offset in kick_offsets:
                new_x = self.current_x + x_offset
                new_y = self.current_y + y_offset
                if self._is_valid_position(self.current_piece, new_rotation, new_x, new_y):
                    self.current_x = new_x
                    self.current_y = new_y
                    self.current_rotation = new_rotation
                    self.stats['total_rotations'] += 1
                    return True
        elif self.current_piece == 'L' or self.current_piece == 'J':
            # L and J pieces need better wall kicks (they're similar)
            kick_offsets = [
                (0, 0),      # Current position
                (-1, 0),     # Left 1
                (1, 0),      # Right 1
                (0, -1),     # Up 1
                (0, 1),      # Down 1
                (-1, -1),    # Up-left
                (1, -1),     # Up-right
                (-1, 1),     # Down-left
                (1, 1),      # Down-right
                (-2, 0),     # Left 2
                (2, 0),      # Right 2
            ]
            
            for x_offset, y_offset in kick_offsets:
                new_x = self.current_x + x_offset
                new_y = self.current_y + y_offset
                if self._is_valid_position(self.current_piece, new_rotation, new_x, new_y):
                    self.current_x = new_x
                    self.current_y = new_y
                    self.current_rotation = new_rotation
                    self.stats['total_rotations'] += 1
                    return True
        else:
            # Try rotation at current position
            if self._is_valid_position(self.current_piece, new_rotation, self.current_x, self.current_y):
                self.current_rotation = new_rotation
                self.stats['total_rotations'] += 1
                return True
            
            # Try wall kicks (shift left/right and up/down)
            kick_offsets = [
                (-1, 0),     # Left 1
                (1, 0),      # Right 1
                (0, -1),     # Up 1
                (0, 1),      # Down 1
                (-2, 0),     # Left 2
                (2, 0),      # Right 2
            ]
            
            for x_offset, y_offset in kick_offsets:
                new_x = self.current_x + x_offset
                new_y = self.current_y + y_offset
                if self._is_valid_position(self.current_piece, new_rotation, new_x, new_y):
                    self.current_x = new_x
                    self.current_y = new_y
                    self.current_rotation = new_rotation
                    self.stats['total_rotations'] += 1
                    return True
        
        return False
    
    def hold(self):
        """Hold current piece."""
        if self.game_over or self.paused or not self.can_hold:
            return False
        
        if self.held_piece is None:
            # First hold - swap current with next
            self.held_piece = self.current_piece
            self._spawn_new_piece()
        else:
            # Swap current with held
            temp = self.current_piece
            self.current_piece = self.held_piece
            self.held_piece = temp
            self.current_x = 3
            self.current_y = 0
            self.current_rotation = 0
        
        self.can_hold = False
        self.stats['hold_uses'] += 1
        return True
    
    def _lock_piece(self):
        """Lock the current piece to the board and check for line clears."""
        self._place_piece(self.current_piece, self.current_rotation, self.current_x, self.current_y)
        lines_cleared = self._clear_lines()
        
        # Store previous lines_cleared to detect change
        previous_lines = self.lines_cleared
        
        if lines_cleared > 0:
            # Update lines cleared
            self.lines_cleared += lines_cleared
            
            # Calculate score (base score * level multiplier)
            base_score = SCORE_VALUES.get(lines_cleared, 0)
            self.score += base_score * self.level
            
            # Level up every 10 lines (level starts at 1, increases every 10 lines)
            new_level = (self.lines_cleared // 10) + 1
            if new_level > self.level:
                self.level = new_level
                # Bonus points for leveling up
                self.score += 1000 * (new_level - 1)
            
            if lines_cleared == 4:
                self.stats['tetris_count'] += 1
                # Bonus for Tetris
                self.score += 1200 * self.level
            
            # Mark that lines were cleared (for therapist roast)
            self.stats['last_lines_cleared'] = lines_cleared
        
        self._spawn_new_piece()
    
    def _clear_lines(self):
        """Clear completed lines and return count."""
        lines_to_clear = []
        
        for y in range(self.BOARD_HEIGHT):
            if all(cell != 0 for cell in self.board[y]):
                lines_to_clear.append(y)
        
        # Remove cleared lines
        for y in reversed(lines_to_clear):
            del self.board[y]
        
        # Add empty lines at top
        for _ in range(len(lines_to_clear)):
            self.board.insert(0, [0 for _ in range(self.BOARD_WIDTH)])
        
        return len(lines_to_clear)
    
    def get_state(self):
        """Get current game state as dictionary."""
        return {
            'board': self.board,
            'current_piece': self.current_piece,
            'current_x': self.current_x,
            'current_y': self.current_y,
            'current_rotation': self.current_rotation,
            'next_piece_type': self.next_piece_type,
            'held_piece': self.held_piece,
            'can_hold': self.can_hold,
            'score': self.score,
            'lines_cleared': self.lines_cleared,
            'level': self.level,
            'game_over': self.game_over,
            'paused': self.paused,
            'stats': self.stats,
        }
    
    def get_drop_preview(self):
        """Get the y position where the piece would land."""
        preview_y = self.current_y
        while self._is_valid_position(self.current_piece, self.current_rotation, 
                                     self.current_x, preview_y + 1):
            preview_y += 1
        return preview_y

