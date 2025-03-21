# build.py
import os
import subprocess
import sys

def compile_for_windows():
    """Compile the game to a Windows executable using PyInstaller"""
    print("Compiling CyberSafe Maze Runner for Windows...")

    # Define PyInstaller command for the main game
    pyinstaller_cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--icon=Game/assets/icon.ico',
        '--name=CyberSafeMazeRunner',
        '--add-data=Game/assets;Game/assets',
        '--hidden-import=pygame',  # ✅ Force inclusion of pygame
        '--hidden-import=socket',  # ✅ Include built-in module to avoid potential issues
        '--hidden-import=threading',
        'main.py'
    ]

    try:
        # Run PyInstaller for the main executable
        subprocess.run(pyinstaller_cmd, check=True)

        # Define PyInstaller command for the cleanup utility
        cleanup_cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--icon=Game/assets/icon.ico',
            '--name=Uninstall_CyberSafeMazeRunner',
            'cleanup.py'
        ]
        subprocess.run(cleanup_cmd, check=True)

        print("\nCompilation successful!")
        print("Executable created at: dist/CyberSafeMazeRunner.exe")
        print("Uninstaller created at: dist/Uninstall_CyberSafeMazeRunner.exe")

    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    compile_for_windows()