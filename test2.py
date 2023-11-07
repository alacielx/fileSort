#https://artifex.com/blog/advanced-text-manipulation-using-pymupdf
import fitz
from PyPDF2 import PdfWriter, PdfReader
pdfRead = PdfReader("1.pdf")
pdfCrop = fitz.open("1.pdf")
pageCrop = pdfCrop[0]

#print(page.get_text())

top_left = pageCrop.rect.x1/3, 0
bottom_right = pageCrop.rect.x1, pageCrop.rect.y1
rect1 = fitz.Rect(top_left, bottom_right)

top_left = pageCrop.rect.x1 / 3, 0
bottom_right = pageCrop.rect.x1, pageCrop.rect.y1
rect2 = fitz.Rect(top_left, bottom_right)

pageCrop.add_redact_annot(rect1)
pageCrop.add_redact_annot(rect2)
pageCrop.apply_redactions()
print(pageCrop.get_text())

pdfCrop.save("2.pdf")

#ebook-convert.exe redacted.pdf redacted.epub