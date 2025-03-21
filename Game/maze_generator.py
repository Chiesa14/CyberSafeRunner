import os
import pygame
import sys
import random


class MazeGenerator:
    def __init__(self, width=15, height=15, cell_size=40):
        """
        Initialize a new maze generator.

        Args:
            width (int): Width of the maze in cells
            height (int): Height of the maze in cells
            cell_size (int): Size of each cell in pixels
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[{"walls": [True, True, True, True], "visited": False}
                      for _ in range(width)] for _ in range(height)]

    def generate(self):
        """
        Generate a maze using the depth-first search algorithm.
        Returns the generated grid.
        """
        stack = []
        current = (0, 0)
        self.grid[0][0]["visited"] = True

        while True:
            neighbors = self.get_unvisited_neighbors(*current)
            if neighbors:
                next_cell = random.choice(neighbors)
                stack.append(current)
                self.remove_walls(current, next_cell)
                current = next_cell
                self.grid[current[1]][current[0]]["visited"] = True
            elif stack:
                current = stack.pop()
            else:
                return self.grid

    def get_unvisited_neighbors(self, x, y):
        """
        Get unvisited neighboring cells.

        Args:
            x (int): X-coordinate of the current cell
            y (int): Y-coordinate of the current cell

        Returns:
            list: List of (x, y) tuples representing unvisited neighbors
        """
        directions = [
            (x, y - 1),  # Top
            (x + 1, y),  # Right
            (x, y + 1),  # Bottom
            (x - 1, y)  # Left
        ]
        return [(nx, ny) for nx, ny in directions
                if 0 <= nx < self.width and 0 <= ny < self.height
                and not self.grid[ny][nx]["visited"]]

    def remove_walls(self, current, next_cell):
        """
        Remove the walls between two adjacent cells.

        Args:
            current (tuple): (x, y) of the current cell
            next_cell (tuple): (x, y) of the next cell
        """
        x1, y1 = current
        x2, y2 = next_cell
        dx, dy = x2 - x1, y2 - y1

        if dx == 1:  # Right
            self.grid[y1][x1]["walls"][1] = False
            self.grid[y2][x2]["walls"][3] = False
        elif dx == -1:  # Left
            self.grid[y1][x1]["walls"][3] = False
            self.grid[y2][x2]["walls"][1] = False
        elif dy == 1:  # Down
            self.grid[y1][x1]["walls"][2] = False
            self.grid[y2][x2]["walls"][0] = False
        elif dy == -1:  # Up
            self.grid[y1][x1]["walls"][0] = False
            self.grid[y2][x2]["walls"][2] = False

    def draw(self, screen):
        """
        Draw the maze on the given screen.

        Args:
            screen (pygame.Surface): Pygame surface to draw on
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                # Calculate pixel coordinates
                px, py = x * self.cell_size, y * self.cell_size

                # Draw walls
                if cell["walls"][0]:  # Top
                    pygame.draw.line(screen, (255, 255, 255),
                                     (px, py),
                                     (px + self.cell_size, py), 2)
                if cell["walls"][1]:  # Right
                    pygame.draw.line(screen, (255, 255, 255),
                                     (px + self.cell_size, py),
                                     (px + self.cell_size, py + self.cell_size), 2)
                if cell["walls"][2]:  # Bottom
                    pygame.draw.line(screen, (255, 255, 255),
                                     (px, py + self.cell_size),
                                     (px + self.cell_size, py + self.cell_size), 2)
                if cell["walls"][3]:  # Left
                    pygame.draw.line(screen, (255, 255, 255),
                                     (px, py),
                                     (px, py + self.cell_size), 2)


if __name__ == "__main__":
    # Test the maze generator
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Maze Generator Test")

    clock = pygame.time.Clock()
    maze = MazeGenerator(20, 15, 40)
    maze.generate()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                maze = MazeGenerator(20, 15, 40)
                maze.generate()

        screen.fill((0, 0, 0))
        maze.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()