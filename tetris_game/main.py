import pygame
import random
import time

# Game constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1], [1, 1]],  # O shape
    [[0, 1, 0], [1, 1, 1]],  # T shape
    [[1, 0, 0], [1, 1, 1]],  # L shape
    [[0, 0, 1], [1, 1, 1]],  # J shape
    [[0, 1, 1], [1, 1, 0]],  # S shape
    [[1, 1, 0], [0, 1, 1]]  # Z shape
]

class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.x = GRID_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def draw(self, screen):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        self.color,
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        0
                    )
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        1
                    )

def create_grid():
    return [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def valid_space(shape, grid, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if y + i >= GRID_HEIGHT or x + j < 0 or x + j >= GRID_WIDTH or grid[y + i][x + j] != (0, 0, 0):
                    return False
    return True

def lock_piece(shape, grid, x, y, color):
    # Adjust y position if piece is at bottom
    while y + len(shape) > GRID_HEIGHT:
        y -= 1
        
    # Adjust y position if piece is at top
    while y < 0:
        y += 1
        
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                # Check if position is within grid bounds
                if 0 <= y + i < GRID_HEIGHT and 0 <= x + j < GRID_WIDTH:
                    grid[y + i][x + j] = color

def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, (255, 255, 255))
    surface.blit(text_surface, (x, y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH + 150, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    
    grid = create_grid()
    current_piece = Tetromino(random.choice(SHAPES))
    next_piece = Tetromino(random.choice(SHAPES))
    score = 0
    last_fall_time = time.time()
    fall_interval = 0.5  # seconds
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if valid_space(current_piece.shape, grid, current_piece.x - 1, current_piece.y):
                        current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid_space(current_piece.shape, grid, current_piece.x + 1, current_piece.y):
                        current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if valid_space(current_piece.shape, grid, current_piece.x, current_piece.y + 2):
                        current_piece.y += 2
                elif event.key == pygame.K_UP:
                    # Rotate shape and convert to list of lists
                    rotated = [list(row) for row in zip(*current_piece.shape[::-1])]
                    if valid_space(rotated, grid, current_piece.x, current_piece.y):
                        current_piece.shape = rotated
        
        # Automatic falling
        current_time = time.time()
        if current_time - last_fall_time > fall_interval:
            current_piece.y += 1
            last_fall_time = current_time
            
            # Check if piece can't move down further
            if not valid_space(current_piece.shape, grid, current_piece.x, current_piece.y + 1):
                # Adjust y position if piece is at bottom
                while not valid_space(current_piece.shape, grid, current_piece.x, current_piece.y):
                    current_piece.y -= 1
                lock_piece(current_piece.shape, grid, current_piece.x, current_piece.y, current_piece.color)
                
                # Check for completed rows
                rows_to_remove = []
                for i, row in enumerate(grid):
                    if all(cell != (0, 0, 0) for cell in row):
                        rows_to_remove.append(i)
                
                # Remove completed rows and move above rows down
                for row_index in sorted(rows_to_remove, reverse=True):
                    del grid[row_index]
                    grid.insert(0, [(0, 0, 0) for _ in range(GRID_WIDTH)])
                
                # Update score based on number of rows cleared
                if len(rows_to_remove) == 1:
                    score += 100
                elif len(rows_to_remove) == 2:
                    score += 300
                elif len(rows_to_remove) == 3:
                    score += 500
                elif len(rows_to_remove) == 4:
                    score += 800
                
                current_piece  = Tetromino(random.choice(SHAPES))  
  
        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw grid
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell != (0, 0, 0):
                    pygame.draw.rect(
                        screen,
                        cell,
                        (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        0
                    )
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                        1
                    )
        
        # Draw current piece
        current_piece.draw(screen)

        # Draw next piece preview
        draw_text(screen, "Next:", 30, SCREEN_WIDTH + 10, 10)
        next_piece.x = GRID_WIDTH + 2
        next_piece.y = 2
        next_piece.draw(screen)
        
        # Draw score
        draw_text(screen, f"Score: {score}", 30, SCREEN_WIDTH + 10, 150)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == '__main__':
    main()
