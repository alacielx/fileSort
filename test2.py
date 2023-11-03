#https://artifex.com/blog/advanced-text-manipulation-using-pymupdf
import fitz

doc = fitz.open("1.pdf")
page = doc[1]

#print(page.get_text())

crop = page.rect.x0, page.rect.x1
rect = fitz.Rect(0,0,100,100)
page.add_redact_annot(rect)
page.apply_redactions()

doc.save("2.pdf")

#ebook-convert.exe redacted.pdf redacted.epub