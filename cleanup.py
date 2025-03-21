import os
import platform
import sys
import winreg
import shutil
import ctypes
import tkinter as tk
from tkinter import messagebox, Label


def is_admin():
    """Check for admin/root privileges."""
    try:
        return os.getuid() == 0 if platform.system() != "Windows" else ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def remove_persistence():
    """Remove all persistence mechanisms"""
    success = True

    try:
        if platform.system() == "Windows":
            # Remove from registry
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                try:
                    winreg.DeleteValue(key, "CyberSafeMaze")
                except FileNotFoundError:
                    pass
                winreg.CloseKey(key)
            except Exception:
                success = False

            # Remove from startup folder
            try:
                startup_path = os.path.join(
                    os.getenv("APPDATA"),
                    "Microsoft", "Windows", "Start Menu",
                    "Programs", "Startup",
                    "CyberSafeMaze.lnk"
                )
                if os.path.exists(startup_path):
                    os.remove(startup_path)
            except Exception:
                success = False

            # Remove application directory
            try:
                app_dir = os.path.join(os.getenv("LOCALAPPDATA"), "CyberSafeMaze")
                if os.path.exists(app_dir):
                    shutil.rmtree(app_dir)
            except Exception:
                success = False

        elif platform.system() == "Linux":
            # Remove from autostart
            try:
                desktop_file = os.path.expanduser("~/.config/autostart/cybersafemaze.desktop")
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
            except Exception:
                success = False
    except Exception:
        success = False

    return success


def create_gui():
    """Create a simple GUI for uninstalling the game"""
    root = tk.Tk()
    root.title("CyberSafe Maze Runner - Uninstaller")
    root.geometry("400x200")
    root.resizable(False, False)

    Label(root, text="CyberSafe Maze Runner", font=("Arial", 16, "bold")).pack(pady=10)
    Label(root, text="This utility will remove all game components\nand undo any changes made to your system.",
          font=("Arial", 10)).pack(pady=10)

    def uninstall():
        root.config(cursor="wait")
        success = remove_persistence()

        if success:
            messagebox.showinfo("Success", "CyberSafe Maze Runner has been completely removed from your system.")
        else:
            messagebox.showwarning("Warning", "Some components could not be removed. Please manually check the system.")

        root.destroy()

    tk.Button(root, text="Uninstall Game", command=uninstall, bg="#ff6b6b", fg="white",
              font=("Arial", 12, "bold")).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    # Check if running with admin privileges
    if not is_admin() and platform.system() == "Windows":
        # Re-run the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        create_gui()