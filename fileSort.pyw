currentVersion = 'v1.0'

from dataclasses import dataclass, field
import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox
import sys
from functions import *

# from getJobNums import *

@dataclass
class Order:
    uniqueCode: str
    orderFileName: list = field(default_factory=list)
    installFileName: str = None
    pdfFolder: str = None
    dxfFolder: str = None
    fsCode: str = None
    fscCode: str = None
    glass: str = None
    fsMatches: list = field(default_factory=list)
    fscMatches: list = field(default_factory=list)
    
    def addFsMatch(self, fileName):
        self.fsMatches.append(fileName)

    def addFscMatch(self, fileName):
        self.fscMatches.append(fileName)
        
    def moveGlassOrders(self):
        glassOrderFilePath = os.path.join(self.pdfFolder, self.orderFileName[0])
        
        batesNumbering(glassOrderFilePath)
        
        if self.glass == "SPECIAL":
            self.orderFileName, glassTypes = separatePdfPages(os.path.join(self.pdfFolder, self.orderFileName[0]))
            
            for glassOrderFile in self.orderFileName:
                glassOrderFilePath = os.path.join(self.pdfFolder, glassOrderFile)
                newOrderFolder = os.path.join(self.pdfFolder, glassTypes[glassOrderFile])
                newGlassOrderFilePath = os.path.join(newOrderFolder, glassOrderFile)
                
                os.makedirs(newOrderFolder, exist_ok=True)
                shutil.move(glassOrderFilePath, newGlassOrderFilePath)
                self.copyDxfs(newOrderFolder)
        else:
            glassOrderFilePath = os.path.join(self.pdfFolder, self.orderFileName[0])
            newOrderFolder = os.path.join(self.pdfFolder, self.glass)
            newGlassOrderFilePath = os.path.join(newOrderFolder, self.orderFileName[0])
            
            os.makedirs(newOrderFolder, exist_ok=True)
            shutil.move(glassOrderFilePath, newGlassOrderFilePath)
            self.copyDxfs(newOrderFolder)
        
        self.delDxfs()
    
    def moveInstalls(self):
        if not self.glass == "MIR":
            installFilePath = os.path.join(self.pdfFolder, self.installFileName)
            installFolder = os.path.join(self.pdfFolder, "Installation Sheets")
            newInstallFilePath = os.path.join(installFolder, self.installFileName)
            
            os.makedirs(installFolder, exist_ok=True)
            shutil.move(installFilePath, newInstallFilePath)
            
    def copyDxfs(self, newOrderFolder):
        for fsFile in self.fsMatches:
            fsFilePath = os.path.join(self.dxfFolder, fsFile)
            newFsFilePath = os.path.join(newOrderFolder, fsFile)
            shutil.copy(fsFilePath, newFsFilePath)
            
        for fscFile in self.fscMatches:
            fscFilePath = os.path.join(self.dxfFolder, fscFile)
            newFscFilePath = os.path.join(newOrderFolder, fscFile)
            shutil.copy(fscFilePath, newFscFilePath)
            
    def delDxfs(self):
        for fsFile in self.fsMatches:
            fsFilePath = os.path.join(self.dxfFolder, fsFile)
            os.remove(fsFilePath)
            
        for fscFile in self.fscMatches:
            fscFilePath = os.path.join(self.dxfFolder, fscFile)
            os.remove(fscFilePath)
                
def batesNumbering(pdfPath):
    global batesNumber
    
    pdf = PdfReader(pdfPath)
    output = PdfWriter()

    stringsToExclude = ["GLASS ORDER", "TEMPLATE"]

    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):
        pageText = pdf.pages[pageNum].extract_text().upper()
        if any(s in pageText for s in stringsToExclude):
            continue

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Set the position where you want to add text (in points from bottom-left)
        x, y = letter[0] - 100, letter[1] - 30  # 1 inch from right, 0.5 inch from top
        can.setFont("Helvetica",20)
        can.drawString(x, y, batesLetter + batesNumber)
        batesNumber = str(int(batesNumber) + 1)
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

    # Update bates number
    configProps["bates_number"] = batesNumber
    updateConfig(configFileName, configProps)
    
def getGlassType(pdfPath):

    pdf = PdfReader(pdfPath)
    output = PdfWriter

    glassPattern = r"\d{1,2}/\d{1,2}\"(?=\s)"

    pageGlassType = {}
    
    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):
        pageText = pdf.pages[pageNum].extract_text().upper()
        thickness = re.findall(glassPattern, pageText)
        if thickness:
            pageGlassType[pageNum] = thickness[0]
        else:
            pageGlassType[pageNum] = None
            
    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):
        currentPage = pdf.pages[pageNum]

        output.add_page(currentPage)

    # Write the output to a new PDF file
    outputStream = open(pdfPath, "wb")
    output.write(outputStream)
    outputStream.close()

    return pageGlassType
    
def separatePdfPages(pdfPath):
    pdf = PdfReader(pdfPath)

    glassPattern = r"\d{1,2}/\d{1,2}\"\s\w+"
    
    newFiles = []
    glassTypes = {}
    # Separate pages
    for pageNum in range(len(pdf.pages)):
        currentPage = pdf.pages[pageNum]
        
        pageText = currentPage.extract_text().upper()
        thickness = re.findall(glassPattern, pageText)
        
        # Try if None
        if thickness:
            thickness = thickness[0]
        else:
            raise ValueError("Thickness is not provided.")

        thickness = str(thickness).replace("/",".")
        thickness = str(thickness).replace("\"","")
        thickness = sanitizeName(thickness)
        
        newPath = os.path.splitext(pdfPath)
        newPath = newPath[0] + " " + str(thickness) + newPath[1]
        
        if os.path.exists(newPath):
            existingPdf = PdfReader(newPath)
            output = PdfWriter()
            for pageNum2 in range(len(existingPdf.pages)):
                existingPage = existingPdf.pages[pageNum2]
                output.add_page(existingPage)
        else:
            output = PdfWriter()
        
        output.add_page(currentPage)
        
        
        
        
        
        newFile = os.path.split(newPath)[1]
        
        if not newFile in newFiles:
            newFiles.append(newFile)
        
        glassTypes[newFile] = thickness
        
        outputStream = open(newPath, "wb")
        output.write(outputStream)
        outputStream.close()
        
    os.remove(pdfPath)
    return newFiles, glassTypes
    
def main():
    # Check if config file exists and has all options
    global configFileName, configProps
    configFileName = 'fileSort.ini'
    configProps = {"bates_letter" : "", "bates_number" : "", "pdf_folder" : "", "dxf_folder" : "",}

    checkConfig(configFileName, configProps)
    configProps = readConfig(configFileName)

    if not configProps['pdf_folder']:
        configProps['pdf_folder'] = askFolderDirectory("Select Glass Order/Install Folder")
    
    if not configProps['dxf_folder']:
        configProps['dxf_folder'] = askFolderDirectory("Select DXF Folder")
    
    if not configProps["bates_letter"]:
        configProps["bates_letter"] = askInput("Bates letter:")

    if not configProps["bates_number"]:
        configProps["bates_number"] = askInput("Last bates number:")

    global batesLetter, batesNumber, pdfFolder, dxfFolder
    batesLetter = configProps["bates_letter"]
    batesNumber = configProps["bates_number"]
    pdfFolder = configProps["pdf_folder"]
    dxfFolder = configProps["dxf_folder"]

    updateConfig(configFileName, configProps)

    # currentDir = os.getcwd()
    # pdfFolder = os.path.join(currentDir, "dxfCheck", "GLASS ORDERS")
    # dxfFolder = os.path.join(currentDir, "dxfCheck", "DXFS")

    # # COMMENT THIS FOR TESTING
    # pdfFolder = r"P:\Alaciel De La Garza --\GLASS ORDERS"
    # dxfFolder = r"P:\Alaciel De La Garza --\DXFS"

    glassOrderPrefix = "Glass Order - "
    installPrefix = "Installation - "
    orders = []

    glass14Initial = ["V", "S"]
    glass38Initial = ["R"]
    glassMirInitial = ["M", "L"]

    # Get pdf name and sort data into list of orders
    for pdfFile in os.listdir(pdfFolder):
        if pdfFile.lower().endswith(".pdf"):
            # Get glass order details
            if pdfFile.startswith(glassOrderPrefix):
                try:
                    pdfCode = os.path.splitext(pdfFile)[0].replace(glassOrderPrefix, "")
                    spaceIndex = pdfCode.find(" ")
                except:
                    continue
                
                uniqueCode = pdfCode[:spaceIndex]

                fsCode = pdfCode[:spaceIndex] + "_FS" if spaceIndex > 0 else pdfCode
                fscCode = pdfCode[:spaceIndex] + "_FSC" if spaceIndex > 0 else pdfCode
                
                pdfCodeInitial = next((char for char in pdfCode[spaceIndex:] if char != ' '), None)
                
                glass = None
                pdfCode = pdfCode.upper()
                if pdfCodeInitial in glassMirInitial:
                    glass = "MIR"
                elif pdfCode.find("HYBRID") > 0 or pdfCode.find("V-PLAT") > 0 or pdfCode.find(" CLR") == -1:
                    glass = "SPECIAL"
                elif pdfCodeInitial in glass14Initial and pdfCode.find(" CLR") > 0:
                    glass = "1.4"
                elif pdfCodeInitial in glass38Initial and pdfCode.find(" CLR") > 0:
                    glass = "3.8"
                
                
                foundOrder = False
                for order in orders:
                    assert isinstance(order, Order)
                    if order.uniqueCode == uniqueCode:
                        foundOrder = True
                        order.orderFileName.append(pdfFile)
                        order.pdfFolder = pdfFolder
                        order.dxfFolder = dxfFolder
                        order.fsCode = fsCode
                        order.fscCode = fscCode
                        order.glass = glass
                        break
                    
                if not foundOrder:
                    orders.append(Order(uniqueCode, orderFileName=[pdfFile], pdfFolder=pdfFolder, dxfFolder=dxfFolder, fsCode=fsCode, fscCode=fscCode, glass=glass))
                    
            # Get installation details
            if pdfFile.startswith(installPrefix):
                try:
                    pdfCode = os.path.splitext(pdfFile)[0].replace(installPrefix, "")
                    spaceIndex = pdfCode.find(" ")
                except:
                    continue
                
                uniqueCode = pdfCode[:spaceIndex]

                foundOrder = False
                for order in orders:
                    assert isinstance(order, Order)
                    if order.uniqueCode == uniqueCode:
                        foundOrder = True
                        order.installFileName = pdfFile
                        break
                if not foundOrder:
                    orders.append(Order(uniqueCode, installFileName=pdfFile))

    # Get dxf codes

    uniqueDxfs = set()

    for dxfFile in os.listdir(dxfFolder):
        if dxfFile.lower().endswith(".dxf"):
            underscoreIndex1 = dxfFile.find("_")
            underscoreIndex2 = dxfFile.find("_", underscoreIndex1 + 1)
            dxfCode = dxfFile[:underscoreIndex1] if underscoreIndex1 > 0 else None
            dxfCodeExt = dxfFile[:underscoreIndex2] if underscoreIndex2 > 0 else None
            
            if dxfCodeExt:
                uniqueDxfs.add(dxfCode)

                for order in orders:
                    assert isinstance(order, Order)
                    if dxfCodeExt == order.fsCode:
                        order.addFsMatch(dxfFile)
                    if dxfCodeExt == order.fscCode:
                        order.addFscMatch(dxfFile)

    # Add missing codes to a list
    matchedDxfs = 0
    missingDxfs = set()
    missingGlassOrder = set()

    for order in orders:
        assert isinstance(order, Order)
        
        # Move Glass Order
        if ((order.fsMatches and order.fscMatches) or (order.glass == "MIR" and (order.fsMatches or order.fscMatches))) and (not order.glass == None):

            # if order.glass == "HYBRID":
            #     pageThickness = getGlassType()
            #     for i in pageThickness:
            #         break
            try:
                order.moveGlassOrders()
                
                order.moveInstalls()

                matchedDxfs+=1
            except:
                continue
        elif not order.orderFileName:
            missingGlassOrder.add(order.installFileName)
        else:
            # Add dxf to missing list
            if not order.fsMatches:
                missingDxfs.add(order.fsCode)
            if not order.fscMatches:
                missingDxfs.add(order.fscCode)

    result = ""

    # if not orders:
    #     result = f"No orders were found."
    # elif missingDxfs:
        
        
        
    if not missingDxfs:
        if not orders:
            result = f"No orders were found."
        elif len(orders) != len(uniqueDxfs):
            result = f"Uneven matches\nPDFs: {len(orders)}, DXFs: {len(uniqueDxfs)}"
        else:
            result = f"Matched {matchedDxfs} order(s)"
    else:
        if matchedDxfs > 0:
            result = f"Matched {matchedDxfs} order(s)\n\n"
        result += "Missing DXFs:\n"
        result += "\n".join(sorted(missingDxfs))
        
    result += f"\nLast bates number used: {int(batesNumber) - 1}"
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Result", result)

if __name__ == "__main__":
    updateExecutable(currentVersion, "fileSort")
    main()