import pygame
import random
import time

# Game constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE
INITIAL_FALL_INTERVAL = 0.5  # seconds
LEVEL_INTERVAL = 10  # lines needed to level up

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
    # Adjust x and y positions to ensure piece is within grid bounds
    while y + len(shape) > GRID_HEIGHT:
        y -= 1
    while y < 0:
        y += 1
    while x + len(shape[0]) > GRID_WIDTH:
        x -= 1
    while x < 0:
        x += 1
        
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                # Final bounds check
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
    lines_cleared = 0
    level = 1
    last_fall_time = time.time()
    fall_interval = INITIAL_FALL_INTERVAL
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause game
                    paused = True
                    while paused:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                                paused = False
                        # Draw pause screen
                        screen.fill((0, 0, 0))
                        # Pause title
                        draw_text(screen, "Paused", 50, SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 100)
                        # Current score
                        draw_text(screen, f"Score: {score}", 30, SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 - 50)
                        # Next piece preview
                        draw_text(screen, "Next:", 30, SCREEN_WIDTH//2 - 30, SCREEN_HEIGHT//2)
                        next_piece.x = GRID_WIDTH//2 - len(next_piece.shape[0])//2
                        next_piece.y = GRID_HEIGHT//2 + 2
                        next_piece.draw(screen)
                        # Resume instructions
                        draw_text(screen, "Press P to resume", 30, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50)
                        pygame.display.flip()
                        clock.tick(5)  # Slow tick rate while paused
                    last_fall_time = time.time()  # Reset fall timer after pause
                elif event.key == pygame.K_LEFT:
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
                    # Adjust x position if rotation would cause out of bounds
                    new_x = current_piece.x
                    if new_x + len(rotated[0]) > GRID_WIDTH:
                        new_x = GRID_WIDTH - len(rotated[0])
                    if new_x < 0:
                        new_x = 0
                    # Check if rotated piece fits in new position
                    if valid_space(rotated, grid, new_x, current_piece.y):
                        current_piece.shape = rotated
                        current_piece.x = new_x
        
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
                
                # Update score and lines cleared
                lines_cleared += len(rows_to_remove)
                if len(rows_to_remove) == 1:
                    score += 100
                elif len(rows_to_remove) == 2:
                    score += 300
                elif len(rows_to_remove) == 3:
                    score += 500
                elif len(rows_to_remove) == 4:
                    score += 800
                
                # Check for level up
                if lines_cleared >= LEVEL_INTERVAL * level:
                    level += 1
                    fall_interval = max(0.1, INITIAL_FALL_INTERVAL - (level-1)*0.05)
                
                current_piece = next_piece
                next_piece = Tetromino(random.choice(SHAPES))
                
                # Reset new piece position
                current_piece.y = 0
                current_piece.x = GRID_WIDTH // 2 - len(current_piece.shape[0]) // 2
                
                # Check if new piece can be placed
                if not valid_space(current_piece.shape, grid, current_piece.x, current_piece.y):
                    # Game over - show final score and restart button
                    while True:
                        screen.fill((0, 0, 0))
                        draw_text(screen, "Game Over!", 50, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100)
                        draw_text(screen, f"Final Score: {score}", 40, SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 50)
                        
                        # Draw restart button
                        restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 + 20, 150, 50)
                        pygame.draw.rect(screen, (0, 255, 0), restart_rect)
                        draw_text(screen, "Restart", 40, SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 35)
                        
                        pygame.display.flip()
                        
                        # Handle events
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                return
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                if restart_rect.collidepoint(event.pos):
                                    # Reset game state
                                    grid = create_grid()
                                    current_piece = Tetromino(random.choice(SHAPES))
                                    next_piece = Tetromino(random.choice(SHAPES))
                                    score = 0
                                    lines_cleared = 0
                                    level = 1
                                    fall_interval = INITIAL_FALL_INTERVAL
                                    last_fall_time = time.time()
                                    break
                        else:
                            continue
                        break
                
                # Reset fall timer for new piece
                last_fall_time = time.time()

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
        
        # Draw borders around play area
        border_color = (255, 255, 255)
        border_width = 2
        # Right border
        pygame.draw.line(
            screen,
            border_color,
            (GRID_WIDTH * BLOCK_SIZE - 1, 0),
            (GRID_WIDTH * BLOCK_SIZE - 1, SCREEN_HEIGHT),
            border_width
        )
        # Left border
        pygame.draw.line(
            screen,
            border_color,
            (0, 0),
            (0, SCREEN_HEIGHT),
            border_width
        )
        # Top border
        pygame.draw.line(
            screen,
            border_color,
            (0, 0),
            (GRID_WIDTH * BLOCK_SIZE, 0),
            border_width
        )
        # Bottom border
        pygame.draw.line(
            screen,
            border_color,
            (0, SCREEN_HEIGHT - 1),
            (GRID_WIDTH * BLOCK_SIZE, SCREEN_HEIGHT - 1),
            border_width
        )
        
        # Draw current piece
        current_piece.draw(screen)

        # Draw next piece preview
        draw_text(screen, "Next:", 30, SCREEN_WIDTH + 10, 10)
        next_piece.x = GRID_WIDTH + 2
        next_piece.y = 2
        next_piece.draw(screen)
        
        # Draw game info
        draw_text(screen, f"Score: {score}", 30, SCREEN_WIDTH + 10, 150)
        draw_text(screen, f"Level: {level}", 30, SCREEN_WIDTH + 10, 200)
        draw_text(screen, f"Speed: {1/fall_interval:.1f}x", 30, SCREEN_WIDTH + 10, 250)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == '__main__':
    main()
