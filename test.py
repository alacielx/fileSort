
import re
from PyPDF2 import PdfWriter, PdfReader
import os
from functions import *
import shutil

def combinePdf(pdfFolder):

    output = PdfWriter()
    
    for pdfFile in os.listdir(pdfFolder):
        if pdfFile.lower().endswith(".pdf"):
            pdfPath = os.path.join(pdfFolder, pdfFile)
            pdf = PdfReader(pdfPath)
            for pageNum in range(len(pdf.pages)):
                currentPage = pdf.pages[pageNum]
                
                output.add_page(currentPage)
            doneFile = os.path.join(pdfFolder,"combined",pdfFile)
            # if not os.path.exists(destination_dir):
            #     os.makedirs(destination_dir)
            shutil.move(pdfPath, doneFile)
                
    outputFile = os.path.join(pdfFolder, "combined", "combined.pdf")
    outputStream = open(outputFile, "wb")
    output.write(outputStream)
    outputStream.close()
    
combinePdf(r"C:\Users\agarza\OneDrive - Arrow Glass Industries\Documents\GitHub\fileSort\combinePdf")