import time
import requests
import os
import psutil
import sys
from tkinter import messagebox
from downloadProgressBar import downloadProgressBar

def is_process_running(process_name):
    process_list = [p.name() for p in psutil.process_iter(attrs=['pid', 'name'])]
    return process_name in process_list

while is_process_running('fileSort.exe'):
    time.sleep(1)

repo_owner = 'alacielx'
repo_name = 'fileSort'
repo_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'

exeName = 'fileSort.exe'
newExeName = 'fileSort_new.exe'
readMeFile = "ReadMe.txt"

response = requests.get(repo_url)
if response.status_code == 200:
    release_data = response.json()
    for asset in release_data.get("assets", []):
        if asset["name"] == exeName:
            exeDownloadUrl = asset["browser_download_url"]
        if asset["name"] == readMeFile:
            readMeDownloadUrl = asset["browser_download_url"]

try:
    downloadProgressBar(exeDownloadUrl, newExeName, title="Updating fileSort...")
    downloadProgressBar(readMeDownloadUrl, readMeFile, title="Downloading readMe.txt...")
except:
    print("Could not download")

# Rename from fileSort_new.exe to fileSort.exe
try:
    if os.path.exists(exeName):
        os.remove(exeName)
    os.rename(newExeName, exeName)
except:
    print("Could not rename file")

messagebox.showinfo("fileSort Updater","Updated fileSort.exe\n\nPlease close this window and run again")
sys.exit()