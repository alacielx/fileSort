## Updater Setup
repoOwner = 'alacielx'
repoName = 'fileSort'
repoUrl = f'https://api.github.com/repos/{repoOwner}/{repoName}/releases/latest'

import time
import requests
import os
import psutil
import sys
import zipfile
import shutil
from tkinter import messagebox
# from downloadProgressBar import downloadProgressBar

def is_process_running(process_name):
    process_list = [os.path.splitext(p.name())[0] for p in psutil.process_iter(attrs=['pid', 'name'])]
    return process_name in process_list

while is_process_running(repoName):
    time.sleep(1)

response = requests.get(repoUrl)
latestVersion = response.json()['tag_name']



if response.status_code == 200:
    # try:
        tempFolderName = "temp"
        if not os.path.exists(tempFolderName):
            os.makedirs(tempFolderName)
            
        latestZipPath = rf"{tempFolderName}\{repoName}.zip"
        with zipfile.ZipFile(latestZipPath, 'w') as zipFile:
            assets = response.json()['assets']
            for asset in assets:
                assetName = asset.get('name')
                downloadUrl = asset.get('browser_download_url')
                if downloadUrl and not assetName == f"{repoName}Updater.pyw":
                    response = requests.get(downloadUrl, stream=True)
                    assetPath = os.path.join(tempFolderName, assetName).replace(os.sep, '/')
                    with open(assetPath, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=128):
                            file.write(chunk)
                    zipFile.write(assetPath, arcname=assetName)
                    os.remove(assetPath)
                    print(f"Downloaded: {assetName}")
            zipFile.extractall()
            zipFile.close()
        # downloadProgressBar(latestZipUrl, latestZipPath, title=f"Updating {repo_name}...")
        # with  zipfile.ZipFile(latestZipPath) as zipFile:
        #     zipFile.extractall()
    # except:
    #     print("Could not download")
    #     sys.exit()
else:
    print("Could not connect to GitHub")
    sys.exit()
    
try:
    if os.path.exists(tempFolderName):
        shutil.rmtree(tempFolderName)
except:
    print("Could not remove file")

# time.sleep(2)
# exec(open("fileSort.pyw").read())
messagebox.showinfo(f"{repoName} Updater",f"Updated {repoName}\n\nPlease close this window and run again")
sys.exit()