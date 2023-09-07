import os
import subprocess
import time
import configparser
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import sys

def read_config_file():
    working_date = config['DEFAULT']['working_date']
    installation_date = config['DEFAULT']['installation_date']

    return working_date, installation_date

def ask_installation_date():
    root = tk.Tk()
    root.withdraw()

    windowTitle = " "
    windowMessage = "Enter Installation Date (ie. XX.XX):"

    new_installation_date = simpledialog.askstring(windowTitle, windowMessage)
    
    if new_installation_date is None:
        sys.exit()
    
    return new_installation_date

def set_installation_date():
    new_installation_date = ask_installation_date()

    config.set("DEFAULT","installation_date",new_installation_date)
    config.set("DEFAULT","working_date",today)

    with open(config_file_name, "w") as configfile:
        config.write(configfile)

########################################################################################################################

folder_path = r"P:\Alaciel De La Garza --\GLASS ORDERS"
files = os.listdir(folder_path)
prefix_to_match = "Glass Order - "
extracted_characters_set = set()
config_file_name = 'pdfScanConfig.ini'
config = configparser.ConfigParser()
config.read(config_file_name)

working_date, installation_date = read_config_file()
time_now = time.strftime("%m.%d.%y_%H.%M.%S")

#Check installation date
today = time.strftime("%m.%d")
if not working_date == today:
    set_installation_date()
    working_date, installation_date = read_config_file()

current_directory = os.getcwd()
current_directory = r"C:\Users\agarza\OneDrive - Arrow Glass Industries\Documents\Scripts"

for file_name in files:
    if file_name.startswith(prefix_to_match):
        extracted_characters_set.add(file_name[len(prefix_to_match):len(prefix_to_match) + 8])

# Create "Job Nums" folder if it doesn't exist
job_nums_path = os.path.join(current_directory, "Job Nums")
if not os.path.exists(job_nums_path):
    os.mkdir(job_nums_path)

# Create installation date folder if it doesn't exist
job_nums_path = os.path.join(job_nums_path, installation_date)
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
