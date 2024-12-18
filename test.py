import os
import sys
import win32com.client
import importlib.util

def create_shortcut(file_path):
    # Get the absolute path to the current script directory

    file_name = os.path.splitext(os.path.split(file_path)[1])[0]
    script_dir = os.path.dirname(file_path)
    

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File does not exist in the current directory.")
        return

    # Get the path to the installed Python executable
    pythonw_exe = os.path.splitext(sys.executable)[0] + "w" + os.path.splitext(sys.executable)[1]  # Path to the Python interpreter running this script

    # Shortcut file name
    shortcut_name = os.path.splitext(file_name)[0] + " - shortcut.lnk"
    shortcut_path = os.path.join(script_dir, shortcut_name)

    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = pythonw_exe
    shortcut.Arguments = f'"{file_path}"'  # Add the target file as an argument
    shortcut.WorkingDirectory = script_dir
    shortcut.IconLocation = os.path.join(script_dir, "filesort.ico")  # Optional: use Python executable icon
    shortcut.Save()

    print(f"Shortcut created: {shortcut_path}")

file_path = os.path.abspath(__file__)
create_shortcut(file_path)
