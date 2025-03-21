import os
import sys
import subprocess
import urllib.request
import time


def check_dependencies():
    """Check if required dependencies are installed and install if missing"""
    print("Checking required dependencies...")
    dependencies = {
        "pygame": check_pygame,
        "socket": lambda: True,  # Built-in module
        "threading": lambda: True,  # Built-in module
    }

    missing_deps = []
    for dep, check_func in dependencies.items():
        print(f"Checking for {dep}...", end=" ")
        if check_func():
            print("Found!")
        else:
            print("Missing!")
            missing_deps.append(dep)

    if missing_deps:
        print("\nSome dependencies are missing. The game needs to install:")
        for dep in missing_deps:
            print(f"- {dep}")

        user_consent = input("\nDo you allow the game to install these dependencies? (y/n): ").strip().lower()
        if user_consent == 'y':
            install_dependencies(missing_deps)
            return True
        else:
            print("Cannot continue without required dependencies.")
            return False
    return True


def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False


def install_dependencies(deps):
    """Install missing dependencies"""
    print("\nInstalling dependencies...")

    # Set up a local server for downloads - simulated here with a path
    local_server = "http://localhost:8000/"  # Replace with your actual local server

    for dep in deps:
        print(f"Installing {dep}...")
        try:
            if dep == "pygame":
                # Try to install using pip first
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                except subprocess.CalledProcessError:
                    # If pip fails, download from local server
                    print(f"Downloading {dep} from local server...")
                    urllib.request.urlretrieve(f"{local_server}{dep}.whl", f"{dep}.whl")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", f"{dep}.whl"])
                    os.remove(f"{dep}.whl")

            print(f"{dep} installed successfully.")
            time.sleep(1)  # Give time to see the message
        except Exception as e:
            print(f"Failed to install {dep}: {e}")
            return False

    print("\nAll dependencies installed successfully!")
    return True