import os
import os.path as path
import sys
import configparser

config = configparser.ConfigParser()

def askFolderDirectory(windowTitle="Select Folder"):
    from tkinter import filedialog
    
    folder_selected = ""

    folder_selected = filedialog.askdirectory(title=windowTitle)
    
    if not folder_selected or not path.exists(folder_selected):
        sys.exit()

    return path.normpath(folder_selected)

def checkConfig(config_file_name, config_props:dict):
    if path.exists(config_file_name):
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
    from tkinter import simpledialog, messagebox
    
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

        
def install_and_import(package, module = None):
    """Installs package

    Args:
        package (string) or (tuple): Tuple gets unpackaged as (package, import_name)
        import_name (string, optional): Defaults to None. If import name is different from package name.
    """
    
    import subprocess
    import importlib.util
    
    if not module:
        module = package
        
    if importlib.util.find_spec(module) is None:
        print(f"Installing {package}.\n")
        
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    else:
        print(f"{package} already installed.\n")
        
    try:
        globals()[module] = importlib.import_module(module)
        print(f"imported {module}")
    except:
        print(f"{module} is already imported.")   
    
def createShortcut(file_path):
    import win32com.client
    file_name = path.splitext(path.split(file_path)[1])[0]
    script_dir = path.dirname(file_path)
    
    # Shortcut file name
    shortcut_name = path.splitext(file_name)[0] + " - shortcut.lnk"
    shortcut_path = path.join(script_dir, shortcut_name)
    
    # Check if the file exists
    if path.exists(shortcut_path) or not path.exists(file_path):
        return

    # Get the path to the installed Pythonw executable
    pythonw_exe = path.join(path.split(sys.executable)[0], "pythonw.exe")  # Path to the Python interpreter running this script

    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = pythonw_exe
    shortcut.Arguments = f'"{file_path}"'
    shortcut.WorkingDirectory = script_dir
    shortcut.IconLocation = path.join(script_dir, path.splitext(file_name)[0] + "Icon.ico")  # Optional: use Python executable icon
    shortcut.Save()

    print(f"Shortcut created: {shortcut_path}")
    
def checkUpdate(currentVersion, repoName):
    import time
    import requests
    import shutil
    
    if path.exists(".git"):
        return
    
    repoOwner = 'alacielx'
    repoUrl = f'https://api.github.com/repos/{repoOwner}/{repoName}/releases/latest'
    
    try:
        response = requests.get(repoUrl)
    except:
        print("Could not connect to GitHub")
        return
    
    tempUpdateFolder = "temp"
    
    if currentVersion < response.json()['tag_name']:
        assetDownloadUrl = None
        if response.status_code == 200:
            assets = response.json()['assets']
            for asset in assets:
                assetFile = asset["name"]
                if path.splitext(assetFile)[0] == repoName + "Updater":
                    assetDownloadUrl = asset["browser_download_url"]
                    break
        else:
            print("Could not connect to GitHub")
            return
        
        if assetDownloadUrl == None:
            return
        
        response = requests.get(assetDownloadUrl, stream=True)
        
        if not path.exists(tempUpdateFolder):
            os.makedirs(tempUpdateFolder)
        tempUpdateFile = path.join(tempUpdateFolder, assetFile)
                
        with open(tempUpdateFile, 'wb') as newAssetFile:
            for chunk in response.iter_content(chunk_size=8192):
                newAssetFile.write(chunk)
        time.sleep(2)
        exec(open(tempUpdateFile).read())
        sys.exit()
    else:
        try:
            if path.exists(tempUpdateFolder):
                shutil.rmtree(tempUpdateFolder)
        except:
            print("Could not remove file")
            
def download_zip(zips):
    import urllib.request
    import zipfile
    
    for key, value in zips.items():
        output_dir = fr"C:\{key}"
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, fr"{key}.zip")
                urllib.request.urlretrieve(value, output_file)

                # Extract the downloaded ZIP file
                with zipfile.ZipFile(output_file, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                
                os.remove(output_file)

                print(fr"{key} has been downloaded and extracted successfully.")
            except Exception as e:
                print(f"An error occurred during the download and extraction of {key}: {str(e)}")
        else:
            print(fr"{key} already installed")

def downloadProgressBar(url, destination_path, title = "Downloading..."):
    import tkinter as tk
    from tkinter import ttk
    import requests
    def read_bytes():
        nonlocal bytes_read
        bytes_read += 500
        progress_var.set((bytes_read / max_bytes) * 100)
        if bytes_read < max_bytes:
            root.after(100, read_bytes)
        else:
            download_file(url, destination_path)

    def download_file(url, destination_path):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(destination_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                root.update_idletasks()

        root.destroy()

    root = tk.Tk()
    root.title(title)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 70) // 2
    root.geometry(f"300x70+{x}+{y}")

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(padx=20, pady=20, fill='both', expand=True)

    bytes_read = 0
    max_bytes = 0

    max_bytes = 50000
    progress_var.set(0)
    read_bytes()

    root.mainloop()