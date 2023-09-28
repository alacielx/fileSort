currentVersion = 'v1.75'

from dataclasses import dataclass, field
import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox
import logging
import sys
from functions import *

@dataclass
class Order:
    uniqueCode: str
    glassOrderFileName: str
    pdfFolder: str
    dxfFolder: str
    fsCode: str
    fscCode: str
    glassThickness: str = None
    glassType: str = None
    showerCode: str = None
    fsMatchesFileName: list = field(default_factory=list)
    fscMatchesFileName: list = field(default_factory=list)
    installationFileName: str = None
    pdfOutputs: dict = field(default_factory=dict)
    skipOrder: bool = False
    
    def addFsMatch(self, fileName):
        self.fsMatchesFileName.append(fileName)

    def addFscMatch(self, fileName):
        self.fscMatchesFileName.append(fileName)
        
    def isOrderValid(self):
        glassOrderFilePath = os.path.join(self.pdfFolder, self.glassOrderFileName)
        
        # Remove extra pages
        processPdfCleanUp(glassOrderFilePath)
        
        self.pdfOutputs = processPdfGlassType(glassOrderFilePath, self)
        
        self.checkMissingInfo()
        
        if self.skipOrder:
            return False
        
        projectNameGlassThickness, projectNameGlassType = self.checkProjectName()
        
        if (self.glassThickness == projectNameGlassThickness or projectNameGlassThickness == None or projectNameGlassThickness == "HYBRID") and (self.glassType == projectNameGlassType or projectNameGlassType == "HYBRID" ):
            return True
        elif projectNameGlassType == None:
            errorMessages.add(rf"{self.uniqueCode}: Enter correct glass type in Project Name.")
            return False
        elif self.glassThickness == "HYBRID":
            errorMessages.add(rf"{self.uniqueCode}: Glass Order has different glass thicknesses.")
            return False
        elif self.glassType == "HYBRID":
            errorMessages.add(rf"{self.uniqueCode}: Glass Order has different glass types.")
            return False
        elif not self.glassThickness == projectNameGlassThickness:
            errorMessages.add(rf"{self.uniqueCode}: Glass thickness does not match shower type.")
            return False
        elif not self.glassType == projectNameGlassType:
            errorMessages.add(rf"{self.uniqueCode}: Glass type does not match Project Name.")
            return False
        else:
            errorMessages.add(rf"{self.uniqueCode}: Please check glass thickness/type.")
            return False
        
    def checkProjectName(self):
        global glassOrderPrefix
        glassThickness = None
        glassType = None
        
        showerCode = str(self.showerCode).upper()
        
        glassThicknessKeywords = {
            "1.4" : ["V", "S", "M", "L"],
            "3.8" : ["R"]
        }
        
        glassTypeKeywords = {
            "CLEAR" : ["CLR", "CL", "CLEAR"],
            "AGI CLEAR" : ["AGI CLR", "AGICLR", "AGI CLEAR", "AGICLEAR", "AGI CL", "AGICL"],
            "RAIN" : ["RN", "RAIN"],
            "OBSCURE" : ["OBS", "OBSCURE"],
            "SATIN" : ["SATIN", "STN", "SAT", "SN"],
            "FROSTED" : ["FROSTED", "FROST"],
            "MIRROR" : ["MIR"]
        }
        
        glassHybridKeywords = ["HYBRID", "VPLAT", "V-PLAT"]
    
        # Check if glass order has glass thickness initial keyword to set glassThickness
        pdfCodeInitial = next((char for char in showerCode if char != ' '), None)
        for thickness, keywords in glassThicknessKeywords.items():
            for keyword in keywords:
                if pdfCodeInitial in keyword:
                    glassThickness = thickness
        
        # Check if glass order has glass type keyword to set glassType
        for type, keywords in glassTypeKeywords.items():
            for keyword in keywords:
                if keyword in showerCode:
                    glassType = type
                    
        # Create a regex pattern that matches isolated keywords
        pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keywords in glassTypeKeywords.values() for keyword in keywords) + r')\b'

        # Check if glass order has glass type keyword to set glassType
        for type, keywords in glassTypeKeywords.items():
            if re.search(pattern, showerCode):
                glassType = type
                break  # If a match is found, exit the loop
        
        # Check if hybrid to change glassThickness and glassType
        for keyword in glassHybridKeywords:
            if keyword in showerCode:
                glassType = "HYBRID"
                glassThickness = "HYBRID"
                
        return glassThickness, glassType
    
    def checkMissingInfo(self):
        
        if self.glassType == "MIRROR":
            if not self.fsMatchesFileName and not self.fscMatchesFileName:
                missingDxfs.add(self.fsCode)
                missingDxfs.add(self.fscCode)
                self.skipOrder = True
        else:
            if not self.fsMatchesFileName:
                missingDxfs.add(self.fsCode)
                self.skipOrder = True
            if not self.fscMatchesFileName:
                missingDxfs.add(self.fscCode)
                self.skipOrder = True
        
        if not self.glassType == "MIRROR" and not self.installationFileName and checkForInstalls == "TRUE":
            missingInstallations.add(self.uniqueCode)
            self.skipOrder = True
            
        return self.skipOrder
                
    def moveGlassOrders(self):
        
        if len(self.pdfOutputs) > 1:
            for glassMakeup, pdfOutput in self.pdfOutputs.items():
                newGlassOrderFileName = os.path.splitext(self.glassOrderFileName)
                newGlassOrderFileName = newGlassOrderFileName[0] + " " + str(glassMakeup) + newGlassOrderFileName[1]
                
                newGlassTypeFolder = os.path.join(self.pdfFolder, glassMakeup)
                os.makedirs(newGlassTypeFolder, exist_ok=True)
                
                newGlassOrderFilePath = os.path.join(newGlassTypeFolder, newGlassOrderFileName)
                
                outputStream = open(newGlassOrderFilePath, "wb")
                pdfOutput.write(outputStream)
                outputStream.close()
                if not self.glassType == "MIRROR":
                    processPdfBatesNumber(newGlassOrderFilePath)
                self.copyDxfs(newGlassTypeFolder)
            
            originalGlassOrderFilePath = os.path.join(self.pdfFolder, self.glassOrderFileName)
            os.remove(originalGlassOrderFilePath)
        else:
            for glassMakeup, pdfOutput in self.pdfOutputs.items():
                glassOrderFilePath = os.path.join(self.pdfFolder, self.glassOrderFileName)
                
                newGlassTypeFolder = os.path.join(self.pdfFolder, glassMakeup)
                os.makedirs(newGlassTypeFolder, exist_ok=True)
                
                newGlassOrderFilePath = os.path.join(newGlassTypeFolder, self.glassOrderFileName)
                
                shutil.move(glassOrderFilePath, newGlassOrderFilePath)
                if not self.glassType == "MIRROR":
                    processPdfBatesNumber(newGlassOrderFilePath)
                self.copyDxfs(newGlassTypeFolder)
        
        self.delDxfs()
    
    def moveInstalls(self):
        if not self.glassType == "MIRROR":
            installFilePath = os.path.join(self.pdfFolder, self.installationFileName)
            installFolder = os.path.join(self.pdfFolder, "Installation Sheets")
            newInstallFilePath = os.path.join(installFolder, self.installationFileName)
            
            os.makedirs(installFolder, exist_ok=True)
            shutil.move(installFilePath, newInstallFilePath)
            
    def copyDxfs(self, newOrderFolder):
        for fsFile in self.fsMatchesFileName:
            fsFilePath = os.path.join(self.dxfFolder, fsFile)
            newFsFilePath = os.path.join(newOrderFolder, fsFile)
            shutil.copy(fsFilePath, newFsFilePath)
            
        for fscFile in self.fscMatchesFileName:
            fscFilePath = os.path.join(self.dxfFolder, fscFile)
            newFscFilePath = os.path.join(newOrderFolder, fscFile)
            shutil.copy(fscFilePath, newFscFilePath)
            
    def delDxfs(self):
        for fsFile in self.fsMatchesFileName:
            fsFilePath = os.path.join(self.dxfFolder, fsFile)
            os.remove(fsFilePath)
            
        for fscFile in self.fscMatchesFileName:
            fscFilePath = os.path.join(self.dxfFolder, fscFile)
            os.remove(fscFilePath)
           
def batesNumberPagesOld(existingPage):
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
    configProps["bates_number"] = batesNumber
    updateConfig(configFileName, configProps)
    
    return existingPage
         
def processPdfCleanUp(pdfPath):
    pdf = PdfReader(pdfPath)
    output = PdfWriter()

    stringsToExclude = ["GLASS ORDER", "TEMPLATE"]

    # Loop through each page of the existing PDF and remove any page with stringsToExclude
    for pageNum in range(len(pdf.pages)):
        pageText = pdf.pages[pageNum].extract_text().upper()
        
        if any(s in pageText for s in stringsToExclude):
            continue
        
        existingPage = pdf.pages[pageNum]
        output.add_page(existingPage)

    # Write the output to a new PDF file
    outputStream = open(pdfPath, "wb")
    output.write(outputStream)
    outputStream.close()
    
def processPdfBatesNumber(pdfPath):
    global batesNumber, minBatesNumber, maxBatesNumber
    pdf = PdfReader(pdfPath)
    output = PdfWriter()

    # Loop through each page of the existing PDF
    for pageNum in range(len(pdf.pages)):

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
    
        # Get the current page from the existing PDF
        existingPage = pdf.pages[pageNum]
        
        newPage = tempPdf.pages[0]
        existingPage.merge_page(newPage)

        output.add_page(existingPage)
        
            # Update bates number
        configProps["bates_number"] = batesNumber
        updateConfig(configFileName, configProps)
    
    # Write the output to a new PDF file
    outputStream = open(pdfPath, "wb")
    output.write(outputStream)
    outputStream.close()
    
def processPdfGlassType(pdfPath, order = Order):
    pdf = PdfReader(pdfPath)

    # Match example: >1/4" AGI Clear< Tempered
    glassPattern = r"\d{1,2}/\d{1,2}\"\s\w+.*?(?= TEMPERED)"
    
    pdfOutputs = {}
    glassThicknesses = set()
    glassTypes = set()
    
    # Separate pages and check glass type
    for pageNum in range(len(pdf.pages)):
        currentPage = pdf.pages[pageNum]
        
        pageText = currentPage.extract_text().upper()
        glassPatternMatch = re.findall(glassPattern, pageText)
        
        
        # Try if None
        try:
            glassPatternMatch = str(glassPatternMatch[0]).upper()
            glassPatternMatch = glassPatternMatch.replace("/", ".")
            glassPatternMatch = sanitizeName(glassPatternMatch, "")
            
            order.glassThickness = glassPatternMatch.split()[0]
            glassThicknesses.add(order.glassThickness)
            order.glassType = " ".join(glassPatternMatch.split()[1:])
            glassTypes.add(order.glassType)
        except:
            raise ValueError(rf"{order.uniqueCode}: No glass type found in Glass Order.")
        
        # Check if already writing a pdf with that glass type
        if not glassPatternMatch in pdfOutputs:
            output = PdfWriter()
        else:
            output = pdfOutputs[glassPatternMatch]

        output.add_page(currentPage)
        
        pdfOutputs[glassPatternMatch] = output
    
    if len(glassThicknesses) > 1:
        order.glassThickness = "HYBRID"
        
    if len(glassTypes) > 1:
        order.glassType = "HYBRID"
        
    return pdfOutputs

######################################################################################################################################################################

def main():
    # Check if config file exists and has all options
    global configFileName, configProps
    configFileName = 'fileSort.ini'
    configProps = {"bates_letter" : "", "bates_number" : "", "pdf_folder" : "", "dxf_folder" : "", "min_bates_number" : "0", "max_bates_number" : "-1", "check_for_installs" : "True"}

    checkConfig(configFileName, configProps)
    configProps = readConfig(configFileName)

    if not configProps['pdf_folder'] or not os.path.exists(configProps['pdf_folder']):
        configProps['pdf_folder'] = askFolderDirectory("Select Glass Order/Install Folder")
    
    if not configProps['dxf_folder'] or not os.path.exists(configProps['dxf_folder']):
        configProps['dxf_folder'] = askFolderDirectory("Select DXF Folder")
    
    if not configProps["bates_letter"]:
        configProps["bates_letter"] = askInput("Bates letter:")

    if not configProps["bates_number"] or not str(configProps["bates_number"]).isnumeric():
        configProps["bates_number"] = askInput("Last bates number:", type = int)

    global batesLetter, batesNumber, pdfFolder, dxfFolder, minBatesNumber, maxBatesNumber, checkForInstalls
    batesLetter = configProps["bates_letter"]
    batesNumber = configProps["bates_number"]
    pdfFolder = configProps["pdf_folder"]
    dxfFolder = configProps["dxf_folder"]
    minBatesNumber = configProps["min_bates_number"]
    maxBatesNumber = configProps["max_bates_number"]
    checkForInstalls = configProps["check_for_installs"].upper()

    updateConfig(configFileName, configProps)

    global missingGlassOrders, missingInstallations, missingDxfs, errorMessages
    missingGlassOrders = set()
    missingInstallations = set()
    missingDxfs = set()
    errorMessages = set()
    
    global glassOrderPrefix
    glassOrderPrefix = "Glass Order - "
    installPrefix = "Installation - "
    orders = []
    
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
                
                showerCode = pdfCode[spaceIndex:]

                fsCode = pdfCode[:spaceIndex] + "_FS" if spaceIndex > 0 else pdfCode
                fscCode = pdfCode[:spaceIndex] + "_FSC" if spaceIndex > 0 else pdfCode
                
                foundOrder = False
                for order in orders:
                    assert isinstance(order, Order)
                    if order.uniqueCode == uniqueCode:
                        if order.glassOrderFileName:
                            errorMessages.add(f"Duplicate order: {uniqueCode}")
                            order.skipOrder = True
                            break
                        else:
                            foundOrder = True
                            order.glassOrderFileName = pdfFile
                            order.pdfFolder = pdfFolder
                            order.dxfFolder = dxfFolder
                            order.fsCode = fsCode
                            order.fscCode = fscCode
                            order.showerCode = showerCode
                            break
                    
                if not foundOrder:
                    orders.append(Order(uniqueCode, pdfFile, pdfFolder, dxfFolder, fsCode, fscCode, showerCode = showerCode))
                    
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
                        order.installationFileName = pdfFile
                        break
                if not foundOrder:
                    orders.append(Order(uniqueCode, None, None, None, None, None, None, installationFileName=pdfFile))

    # Get dxf codes
    extraDxfs = set()
    for dxfFile in os.listdir(dxfFolder):
        if dxfFile.lower().endswith(".dxf"):
            foundOrder = False
            
            underscoreIndex1 = dxfFile.find("_")
            underscoreIndex2 = dxfFile.find("_", underscoreIndex1 + 1)
            dxfCode = dxfFile[:underscoreIndex1] if underscoreIndex1 > 0 else None
            dxfCodeExt = dxfFile[:underscoreIndex2] if underscoreIndex2 > 0 else None
            
            if dxfCodeExt:
                for order in orders:
                    assert isinstance(order, Order)
                    if dxfCodeExt == order.fsCode:
                        order.addFsMatch(dxfFile)
                        foundOrder = True
                    if dxfCodeExt == order.fscCode:
                        order.addFscMatch(dxfFile)
                        foundOrder = True
                        
            if not foundOrder:            
                extraDxfs.add(dxfCodeExt)

    # Check orders to move
    movedOrders = 0
    
    for order in orders:
        assert isinstance(order, Order)
        
        if not order.glassOrderFileName:
            missingGlassOrders.add(order.uniqueCode)
            continue
        
        try:
            # Check glass type and missing information
            if order.isOrderValid() == False:
                continue
            
            order.moveGlassOrders()
            
            if checkForInstalls == "TRUE":
                order.moveInstalls()
                
            movedOrders+=1
            
        except ValueError as e:
            errorMessages.add(e.args[0])
            print(e.args[0])
            continue
                
    result = []

    if movedOrders == 0:
        result.append("No orders were moved.")
    else:
        result.append(f"Moved {movedOrders} order(s)")
        
    if missingGlassOrders:
        result.append(f"{pdfFolder}\nMissing Glass Order(s):\n" + "\n-".join(sorted(missingGlassOrders)))
        
    if missingInstallations:
        result.append(f"{pdfFolder}\nMissing Installation(s):\n" + "\n".join(sorted(missingInstallations)))
    
    if missingDxfs:
        result.append(f"{dxfFolder}\nMissing DXF(s):\n" + "\n".join(sorted(missingDxfs)))
        
    if extraDxfs:
        result.append("Extra DXF(s):\n" + "\n".join(sorted(extraDxfs)))
        
    if errorMessages:
        result.append("Errors:\n" + "\n".join(sorted(errorMessages)))

    result.append(f"Last bates number used: {int(batesNumber) - 1}")
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(f"fileSort {currentVersion}", "\n\n".join(result))

if __name__ == "__main__":
    log_filename = 'error_log.txt'
    logging.basicConfig(filename=log_filename, level=logging.ERROR, format='%(asctime)s - %(levelname)s: %(message)s')

    try:
        updateExecutable(currentVersion, "fileSort")
        main()
    except ValueError as e:
        error_message = e.args[0]
        logging.error(error_message)
        print(error_message)