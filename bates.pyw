from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from functions import *

#Check if config file exists and has all options
config_file_name = 'batesConfig.ini'
config_props = {"bates_number" : "", "bates_letter" : ""}

check_config(config_file_name, config_props)
config_props = read_config_file(config_file_name)

if not config_props["bates_number"]:
    config_props["bates_number"] = ask_input("Last bates number:")

if not config_props["bates_letter"]:
    config_props["bates_letter"] = ask_input("Bates letter:")

bates_number = config_props["bates_number"]
bates_letter = config_props["bates_letter"]

update_config(config_file_name, config_props)

# Read the existing PDF
pdf_path = r'C:\Users\agarza\OneDrive - Arrow Glass Industries\Documents\Scripts\Test\dxfCheck\test.pdf'
pdf = PdfReader(pdf_path)
pdf_path
output = PdfWriter()

# Create the new PDF with Reportlab

strings_to_exclude = ["GLASS ORDER", "TEMPLATE"]

# Loop through each page of the existing PDF
for page_num in range(len(pdf.pages)):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Set the position where you want to add text (in points from bottom-left)
    x, y = letter[0] - 100, letter[1] - 36  # 1 inch from right, 0.5 inch from top
    can.setFont("Helvetica",20)
    can.drawString(x, y, bates_letter + bates_number)
    bates_number = str(int(bates_number) + 1)
    can.save()
    packet.seek(0)
    temp_pdf = PdfReader(packet)
    
    # Get the current page from the existing PDF
    existing_page = pdf.pages[page_num]
    new_page = temp_pdf.pages[0]
    existing_page.merge_page(new_page)

    page_text = pdf.pages[page_num].extract_text().upper()
    if not any(s in page_text for s in strings_to_exclude):
        output.add_page(existing_page)

# Write the output to a new PDF file
output_stream = open(r'C:\Users\agarza\OneDrive - Arrow Glass Industries\Documents\Scripts\Test\dxfCheck\output.pdf', "wb")
output.write(output_stream)
output_stream.close()

print("Text added to PDF.")
