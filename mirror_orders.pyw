import os
import re
import configparser
import time
import tkinter as tk
from tkinter import messagebox

def find_mirror_orders_in_folder(folder_path):
    mirror_orders = []
    for root, _, files in os.walk(folder_path):
        for pdf_file in files:
            if pdf_file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, pdf_file)
                with open(pdf_path, "rb") as file:
                    pdf_content = file.read().decode("utf-8", errors="ignore").upper()
                    if "MIRCT" in pdf_file or "MIRSQCT" in pdf_file:
                        prefix_removed = pdf_file.replace("Glass Order - ", "")
                        mirror_order = re.search(r"\b(\w{8})\b", prefix_removed)
                        if mirror_order and mirror_order.group(1) not in mirror_orders:
                            mirror_orders.append(mirror_order.group(1))

    return mirror_orders

def open_pdfs_with_mirror_orders(mirror_orders, folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

 

    for pdf_file in pdf_files:
        for mirror_order in mirror_orders:
            if mirror_order in pdf_file:
                pdf_path = os.path.join(folder_path, pdf_file)
                os.startfile(pdf_path)
                time.sleep(1)
                break

def read_config_file():
    config_file_name = 'pdfScanConfig.ini'
    config = configparser.ConfigParser()
    config.read(config_file_name)

    pdf_folder = config['DEFAULT']['pdf_folder']
    working_date = config['DEFAULT']['working_date']
    installation_date = config['DEFAULT']['installation_date']
    initials = config['DEFAULT']['initials']
    add_so_number = config['DEFAULT']['add_so_number']

    return pdf_folder, working_date, installation_date, initials, add_so_number


# Search for mirror orders in "P:\Alaciel De La Garza --\GLASS ORDERS\07.26" folder and its subdirectories
_, _, installation_date, _, _ = read_config_file()
source_folder = fr"P:\Alaciel De La Garza --\GLASS ORDERS\{installation_date}"
mirror_orders = find_mirror_orders_in_folder(source_folder)

if mirror_orders:
    
    print("Found mirror orders:", mirror_orders)

    # Search for PDFs with mirror orders in "S:\AlacielG" folder and open them
    target_folder = r"S:\AlacielG"
    open_pdfs_with_mirror_orders(mirror_orders, target_folder)
else:
    messagebox.showinfo("Mirror Orders", "No mirror orders found in the specified folder.")

