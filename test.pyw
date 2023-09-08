from dataclasses import dataclass, field
import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox
import sys
from functions import *

def batesNumberPages(existingPage):
    global batesNumber, minBatesNumber, maxBatesNumber
    
    # Create blank pdf
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Set the position where you want to add text (in points from bottom-left)
    batesText = batesLetter + batesNumber
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
    
    newPage = tempPdf.pages[0]
    existingPage.merge_page(newPage)
    
    # Update bates number
    # configProps["bates_number"] = batesNumber
    # updateConfig(configFileName, configProps)
    
    return existingPage

def processPdf(pdfPath, doBates=True):
    pdf = PdfReader(pdfPath)
    output = PdfWriter()

    stringsToExclude = ["GLASS ORDER", "TEMPLATE"]

    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):
        pageText = pdf.pages[pageNum].extract_text().upper()
        if any(s in pageText for s in stringsToExclude):
            continue

        # Get the current page from the existing PDF
        existingPage = pdf.pages[pageNum]
        
        if doBates == True:
            existingPage = batesNumberPages(existingPage)

        output.add_page(existingPage)

    # Write the output to a new PDF file
    newPdfPath = os.path.splitext(pdfPath)[0] + "_new" + os.path.splitext(pdfPath)[1] 
    outputStream = open(newPdfPath, "wb")
    output.write(outputStream)
    outputStream.close()

batesLetter = 'A'
batesNumber = '0'
minBatesNumber = '0'
maxBatesNumber = '1'
processPdf(r"C:\Users\agarza\OneDrive - Arrow Glass Industries\Documents\GitHub\fileSort\1.pdf")