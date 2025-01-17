import os
from tkinter import simpledialog, messagebox, filedialog
import sys
import configparser
import sys
import requests
import time
import shutil
import win32com.client
import importlib.util
import subprocess
import sys

config = configparser.ConfigParser()

def askFolderDirectory(windowTitle="Select Folder"):
    folder_selected = ""

    folder_selected = filedialog.askdirectory(title=windowTitle)
    
    if not folder_selected or not os.path.exists(folder_selected):
        sys.exit()

    return os.path.normpath(folder_selected)

def checkConfig(config_file_name, config_props:dict):
    if os.path.exists(config_file_name):
        config.read(config_file_name)

    for option, value in config_props.items():
        if not config.has_option("DEFAULT", option):
            config.set('DEFAULT', option, value)
    
    with open(config_file_name, 'w') as config_file:
        config.write(config_file)

def updateConfig(config_file_name, config_props:dict):
    config.read(config_file_name)

    for option, value in config_props.items():
            config.set('DEFAULT', option, value)
    
    with open(config_file_name, 'w') as config_file:
        config.write(config_file)
        config_file.flush()
    
def readConfig(config_file_name):
    config_props = {}

    config.read(config_file_name)
    
    for option, value in config["DEFAULT"].items():
        config_props[option] = value

    return config_props

def askInput(message, windowTitle = " ", type = str):
    user_input = simpledialog.askstring(windowTitle, message)
    
    try:
        type(user_input)
    except:
        messagebox.showinfo(" ", "Please enter correct type")
        user_input = askInput(message, windowTitle, type)
    
    if user_input is None:
        sys.exit()
    
    return user_input

# Function to sanitize file names
def sanitizeName(file_name, character = "_"):
    
    file_name = file_name.split("\n")[0]

    invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    
    # Replace invalid characters and remove at the end of the file name
    for invalid_char in invalid_chars:
        if file_name.endswith(invalid_char) or file_name.endswith(" "):
            file_name = file_name[:-len(invalid_char)]
        else:
            file_name = file_name.replace(invalid_char, character)
    
    return file_name
def install_and_import(package, import_name = None):
    """Installs package

    Args:
        package (string) or (tuple): Tuple gets unpackaged as (package, import_name)
        import_name (string, optional): Defaults to None. If import name is different from package name.
    """
    if type(package) is tuple:
        package, import_name = package
    if not import_name:
        import_name = package
    if importlib.util.find_spec(import_name) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    globals()[package] = importlib.import_module(import_name)
    
def createShortcut(file_path):
    file_name = os.path.splitext(os.path.split(file_path)[1])[0]
    script_dir = os.path.dirname(file_path)
    
    # Shortcut file name
    shortcut_name = os.path.splitext(file_name)[0] + " - shortcut.lnk"
    shortcut_path = os.path.join(script_dir, shortcut_name)
    
    # Check if the file exists
    if os.path.exists(shortcut_path) or not os.path.exists(file_path):
        return

    # Get the path to the installed Pythonw executable
    pythonw_exe = os.path.join(os.path.split(sys.executable)[0], "pythonw.exe")  # Path to the Python interpreter running this script

    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = pythonw_exe
    shortcut.Arguments = f'"{file_path}"'
    shortcut.WorkingDirectory = script_dir
    shortcut.IconLocation = os.path.join(script_dir, os.path.splitext(file_name)[0] + ".ico")  # Optional: use Python executable icon
    shortcut.Save()

    print(f"Shortcut created: {shortcut_path}")
    
def checkUpdate(currentVersion, repoName):
    repoOwner = 'alacielx'
    repoUrl = f'https://api.github.com/repos/{repoOwner}/{repoName}/releases/latest'
    
    try:
        response = requests.get(repoUrl)
    except:
        print("Could not connect to GitHub")
        return
    
    if os.path.exists(".git"):
        return
    
    if currentVersion < response.json()['tag_name']:
        if response.status_code == 200:
            assets = response.json()['assets']
            for asset in assets:
                assetFile = asset["name"]
                if os.path.splitext(assetFile)[0] == repoName + "Updater": 
                    assetDownloadUrl = asset["browser_download_url"]
                    break
        else:
            print("Could not connect to GitHub")
            return
        
        tempUpdateFolder = "temp"
        if not os.path.exists(tempUpdateFolder):
            os.makedirs(tempUpdateFolder)
        tempUpdateFile = os.path.join(tempUpdateFolder, assetFile)
        
        response = requests.get(assetDownloadUrl, stream=True)
        with open(tempUpdateFile, 'wb') as newAssetFile:
            for chunk in response.iter_content(chunk_size=8192):
                newAssetFile.write(chunk)
        time.sleep(2)
        # subprocess.Popen([assetFile])
        # subprocess.Popen(['python', assetFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exec(open(tempUpdateFile).read())
        sys.exit()
    else:
        try:
            if os.path.exists(tempUpdateFolder):
                shutil.rmtree(tempUpdateFolder)
        except:
            print("Could not remove file")