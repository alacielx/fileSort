import fitz  # PyMuPDF

pdf_path = r'testData\test.pdf'
output_path = r'testData\output.pdf'  # Save the modified PDF to a new file

# # Open the original PDF
# pdf = fitz.open(pdf_path)

# # Metadata field to check and update
# field_name = 'batesNumbered'

# # Create a new PDF document
# new_pdf = fitz.open()

# # Copy pages from the original PDF to the new PDF
# for page_num in range(len(pdf)):
#     page = pdf[page_num]
#     new_page = new_pdf.new_page(width=page.rect.width, height=page.rect.height)
#     new_page.show_pdf_page(page.rect, pdf, page_num)

# # Check if the custom metadata field exists
# if field_name in new_pdf.metadata and new_pdf.metadata[field_name]:
#     print(f"The value of '{field_name}' is: {new_pdf.metadata[field_name]}")
# else:
#     print(f"'{field_name}' is empty")
#     new_pdf.metadata[field_name] = 'True'
    
# # Save the new PDF
# new_pdf.save(output_path)

pdf = fitz.open(output_path)

# # Metadata field to check and update
# field_name = 'batesNumbered'

# # Check if the custom metadata field exists
# if field_name in pdf.metadata and pdf.metadata[field_name]:
#     print(f"The value of '{field_name}' is: {pdf.metadata[field_name]}")
# else:
#     print(f"'{field_name}' is empty")


# Close both the original and new PDFs
pdf.close()
# new_pdf.close()
