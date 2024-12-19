import os
import subprocess
import time
import configparser
from tkinter import messagebox
from tkinter import filedialog
import sys

from functions import createShortcut

def askFolderDirectory(windowTitle="Select Folder"):
    folder_selected = ""

    folder_selected = filedialog.askdirectory(title=windowTitle)
    
    if not folder_selected or not os.path.exists(folder_selected):
        sys.exit()

    return os.path.normpath(folder_selected)

########################################################################################################################

createShortcut(os.path.abspath(__file__))

config_file_name = 'fileSort.ini'
config = configparser.ConfigParser()
config.read(config_file_name)

try:
    folder_path = config['DEFAULT']['pdf_folder']
except:
    folder_path = None

if not folder_path or not os.path.exists(folder_path):
    folder_path = askFolderDirectory("Select PDF Folder")

files = os.listdir(folder_path)
prefix_to_match = "Glass Order - "
extracted_characters_set = set()

today = time.strftime("%m.%d")
time_now = time.strftime("%m.%d.%y_%H.%M.%S")

current_directory = os.getcwd()
# current_directory = r"C:\Users\agarza\OneDrive - Arrow Glass Industries\Documents\Scripts"

for file_name in files:
    if file_name.startswith(prefix_to_match):
        minimum_spacer_index = [file_name.find("-",len(prefix_to_match)), file_name.find(",",len(prefix_to_match)),file_name.find(" ",len(prefix_to_match))]
        minimum_spacer_index = [x for x in minimum_spacer_index if x > 0]
        order_number = file_name[len(prefix_to_match):min(minimum_spacer_index)]
        extracted_characters_set.add(order_number)

# Create "Job Nums" folder if it doesn't exist
job_nums_path = os.path.join(current_directory, "Job Nums")
if not os.path.exists(job_nums_path):
    os.mkdir(job_nums_path)

# Create installation date folder if it doesn't exist
job_nums_path = os.path.join(job_nums_path, today)
if not os.path.exists(job_nums_path):
    os.mkdir(job_nums_path)

# Create text file name
job_nums_path = os.path.join(job_nums_path, f"jobNums_{time_now}_({len(extracted_characters_set)}).txt")

# Write the extracted characters to the text file
if not len(extracted_characters_set) == 0:
    with open(job_nums_path, "w") as file:
        file.write(", ".join(extracted_characters_set))
else:
    messagebox.showinfo("Get Job Nums", "No Glass Orders")

# Open the text file in the default associated program
subprocess.Popen([job_nums_path], shell=True)
