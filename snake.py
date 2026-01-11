import pygame
import random
import json
import os
from enum import Enum

# Constants
GRID_SIZE = 20
GRID_COUNT = 30
WINDOW_SIZE = (GRID_SIZE * GRID_COUNT, GRID_SIZE * GRID_COUNT + 40)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (80, 80, 80)
BLUE = (0, 0, 255)


class GameMode(Enum):
    NORMAL = "Normal"
    STATUE = "Statue"


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.font_large = pygame.font.SysFont(None, 72)

        # Game state
        self.game_mode = None
        self.game_speed = 150  # Default to medium speed
        self.selecting_mode = True
        self.selecting_speed = False
        self.game_over = False
        self.waiting_for_input = True  # Start waiting for input
        self.score = 0
        self.high_score = 0
        self.snake = []
        self.direction = None
        self.next_directions = []
        self.food = (0, 0)
        self.statues = set()
        self.cracked_statues = {}
        self.new_statues = set()

        # Initialize game
        self.reset_game()
        self.load_high_scores()

    def reset_game(self):
        """Reset the game state while preserving mode and speed"""
        center = GRID_COUNT // 2
        self.snake = [(center, center)]
        self.direction = None
        self.next_directions = []
        self.food = self.spawn_food()
        self.statues = set()
        self.cracked_statues = {}
        self.new_statues = set()
        self.score = 0
        self.game_over = False
        self.waiting_for_input = True
        self.load_high_scores()

    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists('highscores.json'):
                with open('highscores.json', 'r') as f:
                    highscores = json.load(f)
                    if self.game_mode:
                        self.high_score = highscores.get(self.game_mode.name, 0)
        except:
            self.high_score = 0

    def save_high_scores(self):
        """Save high scores to file"""
        try:
            highscores = {}
            if os.path.exists('highscores.json'):
                with open('highscores.json', 'r') as f:
                    highscores = json.load(f)

            if self.game_mode:
                highscores[self.game_mode.name] = max(
                    highscores.get(self.game_mode.name, 0),
                    self.high_score
                )

            with open('highscores.json', 'w') as f:
                json.dump(highscores, f)
        except Exception as e:
            print(f"Error saving high scores: {e}")

    def spawn_food(self):
        """Spawn food at a random position"""
        while True:
            pos = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if (pos not in self.snake and
                    pos not in self.statues and
                    pos not in self.cracked_statues):
                return pos

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.selecting_speed:
                        self.selecting_speed = False
                        self.selecting_mode = True
                        return True
                    return False

                # Handle home screen
                if event.key == pygame.K_h and not (self.selecting_mode or self.selecting_speed):
                    self.selecting_mode = True
                    return True

                # Handle restart
                if event.key == pygame.K_r and (self.game_over or self.waiting_for_input):
                    self.reset_game()
                    return True

                # Handle mode selection
                if self.selecting_mode:
                    if event.key == pygame.K_1:
                        self.game_mode = GameMode.NORMAL
                        self.selecting_mode = False
                        self.selecting_speed = True
                        return True
                    elif event.key == pygame.K_2:
                        self.game_mode = GameMode.STATUE
                        self.selecting_mode = False
                        self.selecting_speed = True
                        return True

                # Handle speed selection
                elif self.selecting_speed:
                    if event.key == pygame.K_1:
                        self.game_speed = 200  # Slow
                        self.selecting_speed = False
                        self.waiting_for_input = True
                        return True
                    elif event.key == pygame.K_2:
                        self.game_speed = 150  # Medium
                        self.selecting_speed = False
                        self.waiting_for_input = True
                        return True
                    elif event.key == pygame.K_3:
                        self.game_speed = 100  # Fast
                        self.selecting_speed = False
                        self.waiting_for_input = True
                        return True

                # Handle game start
                elif self.waiting_for_input and event.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    self.waiting_for_input = False
                    # Set initial direction based on first key press
                    if event.key == pygame.K_UP:
                        self.direction = Direction.UP
                    elif event.key == pygame.K_DOWN:
                        self.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT:
                        self.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT:
                        self.direction = Direction.RIGHT
                    return True

                # Handle direction changes during game
                if not self.game_over and not self.waiting_for_input:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.next_directions.append(Direction.UP)
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.next_directions.append(Direction.DOWN)
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.next_directions.append(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.next_directions.append(Direction.RIGHT)

        return True

    def _process_direction_queue(self):
        """Process the next direction from the input queue if available"""
        if self.next_directions:
            next_dir = self.next_directions.pop(0)
            # Only change direction if it's valid (not opposite of current direction)
            if (self.direction is None or
                    (next_dir.value[0] * -1, next_dir.value[1] * -1) != self.direction.value):
                self.direction = next_dir

    def _check_collision(self, position):
        """Check if the given position collides with walls, self, or statues"""
        x, y = position
        
        # Allow the snake to go behind the score area at the bottom
        # The score area is the bottom 40 pixels of the window
        score_area_start = (WINDOW_SIZE[1] - 40) // GRID_SIZE
        
        # Check for wall collisions (except bottom where score is)
        if (x < 0 or x >= GRID_COUNT or 
            y < 0 or (y >= GRID_COUNT and y < score_area_start)):
            return True
            
        # Check for self-collision
        if position in self.snake:
            return True
        
        # Check for statue collisions (only in Statue mode)
        if (self.game_mode == GameMode.STATUE and 
                position in self.statues and 
                position not in self.cracked_statues):
            return True
            
        return False

    def _handle_collision(self, position):
        """Handle collision with the given position"""
        if position in self.cracked_statues:
            # Remove the cracked statue
            if position in self.statues:
                self.statues.remove(position)
            if position in self.cracked_statues:
                del self.cracked_statues[position]
            if position in self.new_statues:
                self.new_statues.remove(position)
            return True
        return False

    def _update_high_score(self):
        """Update high score if current score is higher"""
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_scores()

    def _handle_food_eaten(self):
        """Handle logic when food is eaten"""
        self.score += 1
        self._update_high_score()

        if self.game_mode == GameMode.STATUE and len(self.snake) > 1:
            self._create_statues()
            self._handle_statue_cracking()

        self.food = self.spawn_food()

    def update(self):
        """Update game state"""
        if self.game_over or self.waiting_for_input or self.selecting_mode or self.selecting_speed:
            return

        self._process_direction_queue()

        if self.direction is None:
            return

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Check for collisions
        if self._check_collision(new_head):
            self.game_over = True
            self._update_high_score()
            return

        # Handle cracked statue collision
        if self.game_mode == GameMode.STATUE:
            self._handle_collision(new_head)

        # Add new head
        self.snake.insert(0, new_head)

        # Check if food is eaten
        if new_head == self.food:
            self._handle_food_eaten()
        else:
            # Only remove tail if no food was eaten
            self.snake.pop()

    def _create_statues(self):
        """Create statues from the snake's body (excluding head)"""
        if len(self.snake) <= 1:
            return

        # Clear previous new statues
        self.new_statues.clear()

        # Convert all segments except the head to statues
        for i in range(1, len(self.snake)):
            pos = self.snake[i]
            self.statues.add(pos)
            self.new_statues.add(pos)

    def _handle_statue_cracking(self):
        """Handle statue cracking logic"""
        if self.game_mode != GameMode.STATUE or len(self.statues) == 0 or self.score < 2:
            return

        # Start with 1 crack, increase more slowly with score
        base_crack_count = 1 + (self.score // 3)  # Reduced from //2 to //3

        # First, remove any statues that have been cracked twice
        to_remove = [pos for pos, count in self.cracked_statues.items() if count >= 2]
        for pos in to_remove:
            if pos in self.statues:
                self.statues.remove(pos)
            if pos in self.cracked_statues:
                del self.cracked_statues[pos]
            if pos in self.new_statues:
                self.new_statues.remove(pos)

        # Reduced chance of any cracking happening at all (from 80% to 50%)
        if random.random() < 0.5:
            # Get crackable statues (not new and not already cracked)
            crackable_statues = [pos for pos in self.statues
                               if pos not in self.new_statues and
                               pos not in self.cracked_statues]

            if crackable_statues:
                num_to_crack = min(base_crack_count, len(crackable_statues))
                random.shuffle(crackable_statues)

                # Only process up to num_to_crack statues
                for pos in crackable_statues[:num_to_crack]:
                    # Reduced chance of each individual statue cracking (from 90% to 60%)
                    if random.random() < 0.6:
                        if pos in self.cracked_statues:
                            self.cracked_statues[pos] += 1
                        else:
                            self.cracked_statues[pos] = 1

    def draw(self):
        """Draw the game"""
        self.screen.fill(BLACK)

        if self.selecting_mode:
            self.draw_mode_selection()
        elif self.selecting_speed:
            self.draw_speed_selection()
        else:
            self.draw_game()

        pygame.display.flip()

    def draw_mode_selection(self):
        """Draw the game mode selection screen"""
        title = self.font_large.render("SNAKE GAME", True, GREEN)
        mode1 = self.font.render("1 - Normal Mode", True, WHITE)
        mode2 = self.font.render("2 - Statue Mode", True, WHITE)
        instructions = self.font.render("Select a game mode", True, WHITE)

        self.screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, 100))
        self.screen.blit(mode1, (WINDOW_SIZE[0] // 2 - mode1.get_width() // 2, 250))
        self.screen.blit(mode2, (WINDOW_SIZE[0] // 2 - mode2.get_width() // 2, 300))
        self.screen.blit(instructions, (WINDOW_SIZE[0] // 2 - instructions.get_width() // 2, 400))

    def draw_speed_selection(self):
        """Draw the speed selection screen"""
        title = self.font_large.render("SELECT SPEED", True, GREEN)
        speed1 = self.font.render("1 - Slow", True, WHITE)
        speed2 = self.font.render("2 - Medium", True, WHITE)
        speed3 = self.font.render("3 - Fast", True, WHITE)
        instructions = self.font.render("Choose game speed", True, WHITE)

        self.screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, 100))
        self.screen.blit(speed1, (WINDOW_SIZE[0] // 2 - speed1.get_width() // 2, 250))
        self.screen.blit(speed2, (WINDOW_SIZE[0] // 2 - speed2.get_width() // 2, 300))
        self.screen.blit(speed3, (WINDOW_SIZE[0] // 2 - speed3.get_width() // 2, 350))
        self.screen.blit(instructions, (WINDOW_SIZE[0] // 2 - instructions.get_width() // 2, 450))

    def draw_game(self):
        """Draw the main game"""
        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(self.screen, RED, food_rect)

        # Draw snake
        for i, segment in enumerate(self.snake):
            color = GREEN if i == 0 else (0, 200, 0)  # Head is brighter green
            segment_rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, color, segment_rect)
            pygame.draw.rect(self.screen, (0, 100, 0), segment_rect, 1)  # Border

            # Draw eyes on the head
            if i == 0 and self.direction:  # Only if it's the head and direction is set
                eye_radius = GRID_SIZE // 5
                pupil_radius = eye_radius // 2
                center_x = segment[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = segment[1] * GRID_SIZE + GRID_SIZE // 2
                offset = GRID_SIZE // 4

                # Calculate eye positions based on direction
                if self.direction == Direction.RIGHT:
                    left_eye = (center_x + offset, center_y - offset)
                    right_eye = (center_x + offset, center_y + offset)
                elif self.direction == Direction.LEFT:
                    left_eye = (center_x - offset, center_y - offset)
                    right_eye = (center_x - offset, center_y + offset)
                elif self.direction == Direction.UP:
                    left_eye = (center_x - offset, center_y - offset)
                    right_eye = (center_x + offset, center_y - offset)
                else:  # DOWN
                    left_eye = (center_x - offset, center_y + offset)
                    right_eye = (center_x + offset, center_y + offset)

                # Draw eyes (white with black pupils)
                pygame.draw.circle(self.screen, WHITE, left_eye, eye_radius)
                pygame.draw.circle(self.screen, BLACK, left_eye, pupil_radius)
                pygame.draw.circle(self.screen, WHITE, right_eye, eye_radius)
                pygame.draw.circle(self.screen, BLACK, right_eye, pupil_radius)

        # Draw statues
        if self.game_mode == GameMode.STATUE:
            for pos in self.statues:
                # Draw statue
                statue_rect = pygame.Rect(
                    pos[0] * GRID_SIZE,
                    pos[1] * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(self.screen, GRAY, statue_rect)

                # Draw crack if statue is cracked
                if pos in self.cracked_statues:
                    # Draw X for cracked statue
                    x, y = pos[0] * GRID_SIZE, pos[1] * GRID_SIZE
                    pygame.draw.line(self.screen, DARK_GRAY,
                                     (x + 2, y + 2),
                                     (x + GRID_SIZE - 2, y + GRID_SIZE - 2), 4)
                    pygame.draw.line(self.screen, DARK_GRAY,
                                     (x + GRID_SIZE - 2, y + 2),
                                     (x + 2, y + GRID_SIZE - 2), 4)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        speed_text = self.font.render(f"Speed: {3 - (self.game_speed - 100) // 50}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))
        self.screen.blit(speed_text, (10, 90))

        if self.game_over:
            game_over_surface = self.font.render("GAME OVER - Press R to restart or H for home", True, WHITE)
            self.screen.blit(game_over_surface,
                             (WINDOW_SIZE[0] // 2 - game_over_surface.get_width() // 2,
                              WINDOW_SIZE[1] // 2))

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            if not self.handle_events():
                running = False

            # Update game state
            self.update()

            # Draw everything
            self.draw()

            # Cap the frame rate
            self.clock.tick(60)

            # Control game speed
            if not (self.selecting_mode or self.selecting_speed or self.waiting_for_input or self.game_over):
                pygame.time.delay(self.game_speed)

        pygame.quit()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
