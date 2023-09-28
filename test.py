currentVersion = 'v1.6'

from dataclasses import dataclass, field
import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox
import sys
from functions import *

def batesNumberPages(pdfPath):
    batesNumber = "1000"
    minBatesNumber = "0"
    maxBatesNumber = "-1"
    pdf = PdfReader(pdfPath)
    output = PdfWriter()

    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):

        # Create blank pdf
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Set the position where you want to add text (in points from bottom-left)
        batesText = "A" + batesNumber
        batesTextWidth = can.stringWidth(batesText, "Helvetica", 20)
        
        x, y = letter[0] - 40 - batesTextWidth, letter[1] - 30  # 1 inch from right, 0.5 inch from top
        can.setFont("Helvetica",20)
        can.drawString(x, y, batesText)
        
        if maxBatesNumber == '-1':
            batesNumber = str(int(batesNumber) + 1)
        else:
            batesNumber = str(int(batesNumber) + 1) if int(batesNumber)  < int(maxBatesNumber) else minBatesNumber
            
        can.save()
        packet.seek(0)
        tempPdf = PdfReader(packet)
    
        # Get the current page from the existing PDF
        existingPage = pdf.pages[pageNum]
        
        newPage = tempPdf.pages[0]
        existingPage.merge_page(newPage)

        output.add_page(existingPage)
    
    # Write the output to a new PDF file
    outputStream = open(pdfPath, "wb")
    output.write(outputStream)
    outputStream.close()
    
batesNumberPages(r"P:\Alaciel De La Garza --\1.pdf")