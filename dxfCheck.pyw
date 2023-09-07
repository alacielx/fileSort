from dataclasses import dataclass, field
import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox
from functions import *
from getJobNums import *

@dataclass
class Order:
    uniqueCode: str
    orderFileName: str = None
    installFileName: str = None
    fsCode: str = None
    fscCode: str = None
    glass: str = None
    fsMatches: list = field(default_factory=list)
    fscMatches: list = field(default_factory=list)
    
    def addFsMatch(self, fileName):
        self.fsMatches.append(fileName)

    def addFscMatch(self, fileName):
        self.fscMatches.append(fileName)

def batesNumber(pdfPath):
    
    #Check if config file exists and has all options
    configFileName = 'batesConfig.ini'
    configProps = {"bates_letter" : "", "bates_number" : ""}

    checkConfig(configFileName, configProps)
    configProps = readConfig(configFileName)

    if not configProps["bates_letter"]:
        configProps["bates_letter"] = askInput("Bates letter:")

    if not configProps["bates_number"]:
        configProps["bates_number"] = askInput("Last bates number:")

    batesLetter = configProps["bates_letter"]
    batesNumber = configProps["bates_number"]

    updateConfig(configFileName, configProps)

    pdf = PdfReader(pdfPath)
    pdfPath
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

    glassPattern = r"\b\d{1,2}/\d{1,2}\""
    pageGlassType = {}
    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):
        pageText = pdf.pages[pageNum].extract_text().upper()
        pageGlassType[pageNum] = re.findall(glassPattern, pageText)

    return pageGlassType
    
def main():
    currentDir = os.getcwd()
    pdfFolder = os.path.join(currentDir,"dxfCheck","GLASS ORDERS")
    dxfFolder = os.path.join(currentDir,"dxfCheck","DXFS")

    # COMMENT THIS FOR TESTING
    pdfFolder = r"P:\Alaciel De La Garza --\GLASS ORDERS"
    dxfFolder = r"P:\Alaciel De La Garza --\DXFS"

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
            
                ###### ANTQ MIRROR
                ###### V PLAT // HYBRID
                glass = None
                pdfCode = pdfCode.upper()
                if pdfCode.find("HYBRID") > 0 or pdfCode.find("V-PLAT") > 0:
                    glass = "HYBRID"
                elif pdfCode[spaceIndex + 1] in glassMirInitial:
                    glass = "MIR"
                elif pdfCode[spaceIndex + 1] in glass14Initial and pdfCode.find(" CLR") > 0:
                    glass = "1.4"
                elif pdfCode[spaceIndex + 1] in glass38Initial and pdfCode.find(" CLR") > 0:
                    glass = "3.8"
                
                foundOrder = False
                for order in orders:
                    assert isinstance(order, Order)
                    if order.uniqueCode == uniqueCode:
                        foundOrder = True
                        order.orderFileName = pdfFile
                        order.fsCode = fsCode
                        order.fscCode = fscCode
                        order.glass = glass
                        break
                if not foundOrder:
                    orders.append(Order(uniqueCode, pdfFile, None, fsCode, fscCode, glass))
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
                    orders.append(Order(uniqueCode, None, pdfFile))

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

    for order in orders:
        assert isinstance(order, Order)
        # Move Glass Order that has a glass type and is not HYBRID
        if (order.fsMatches and order.fscMatches) and (order.glass == "HYBRID"):
            getGlassType()

            break

        if (order.fsMatches and order.fscMatches) or (order.glass == "MIR" and (order.fsMatches or order.fscMatches)):

            
            glassOrderFilePath = os.path.join(pdfFolder,order.orderFileName)
            orderGlassFolder = os.path.join(pdfFolder,str(order.glass))
            newGlassOrderFilePath = os.path.join(orderGlassFolder,order.orderFileName)
            
            if not order.glass == "MIR":
                installFilePath = os.path.join(pdfFolder,order.installFileName)
                installFolder = os.path.join(pdfFolder,"Installation Sheets")
                newInstallFilePath = os.path.join(installFolder,order.installFileName)
            
            batesNumber(glassOrderFilePath)
            
            # Create folders and move Glass Order and Installs if not MIR
            os.makedirs(orderGlassFolder, exist_ok=True)
            shutil.move(glassOrderFilePath, newGlassOrderFilePath)
            
            if not order.glass == "MIR":
                os.makedirs(installFolder, exist_ok=True)
                shutil.move(installFilePath, newInstallFilePath)
            
            # Move DXFs for Glass Order
            for fsFile in order.fsMatches:
                fsFilePath = os.path.join(dxfFolder,fsFile)
                newFsFilePath = os.path.join(orderGlassFolder,fsFile)
                shutil.move(fsFilePath, newFsFilePath)
            
            for fscFile in order.fscMatches:
                fscFilePath = os.path.join(dxfFolder,fscFile)
                newFscFilePath = os.path.join(orderGlassFolder,fscFile)
                shutil.move(fscFilePath, newFscFilePath)

            matchedDxfs+=1
        else:
            # Add dxf to missing list
            if not order.fsMatches:
                missingDxfs.add(order.fsCode)
            if not order.fscMatches:
                missingDxfs.add(order.fscCode)

    result = ""
    # if matchedDxfs > 0:
    #         result += f"Matched {matchedDxfs} order(s)\n\n"
    # if missingDxfs:
    #     result += "Missing DXFs:\n"
    #     result += "\n".join(sorted(missingDxfs))
    # else:
    #     None

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
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Result", result)

if __name__ == "__main__":
    main()