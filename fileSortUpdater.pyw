## Updater Setup
repo_owner = 'alacielx'
repo_name = 'fileSort'
repo_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'

import time
import requests
import os
import psutil
import sys
import zipfile
import io
from tkinter import messagebox
from downloadProgressBar import downloadProgressBar

def is_process_running(process_name):
    process_list = [os.path.splitext(p.name())[0] for p in psutil.process_iter(attrs=['pid', 'name'])]
    return process_name in process_list

while is_process_running(repo_name):
    time.sleep(1)

response = requests.get(repo_url)
latestVersion = response.json()['tag_name']

latestZipUrl = f"https://github.com/alacielx/fileSort/archive/{latestVersion}.zip"
latestZipPath = f"{repo_name}.zip"

if response.status_code == 200:
    try:
        downloadProgressBar(latestZipUrl, latestZipPath, title=f"Updating {repo_name}...")
        with  zipfile.ZipFile(latestZipPath) as zipFile:
            zipFile.extractall()
    except:
        print("Could not download")
        sys.exit()
else:
    print("Could not connect to GitHub")
    sys.exit()
    



# Rename from fileSort_new.exe to fileSort.exe
try:
    if os.path.exists(latestZipPath):
        os.remove(latestZipPath)
    # os.rename(newExeName, exeName)
except:
    print("Could not remove file")

messagebox.showinfo(f"{repo_name} Updater",f"Updated {repo_name}\n\nPlease close this window and run again")
sys.exit()