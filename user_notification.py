import tkinter as tk
from tkinter import messagebox


def show_disclaimer():
    """Display a disclaimer to the user about the game's behavior"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    title = "CyberSafe Maze Runner - Disclaimer"
    message = """
EDUCATIONAL DISCLAIMER

This game is designed for educational purposes to demonstrate cybersecurity concepts.

By continuing, you acknowledge and consent to the following:

1. This application will check for and install any missing dependencies
2. The game will create temporary files in the background for smooth gameplay
3. All components will be completely removed when you uninstall the game
4. This application is for EDUCATIONAL PURPOSES ONLY

Do you wish to continue?
    """

    user_consent = messagebox.askyesno(title, message)
    root.destroy()

    return user_consent


if __name__ == "__main__":
    show_disclaimer()