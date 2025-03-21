# This file makes the Game directory a Python package
# Import key components to make them available when importing the package
from .game import Game
from .maze_generator import MazeGenerator

__all__ = ['Game', 'MazeGenerator']