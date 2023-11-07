from PyPDF2 import PdfReader

reader = PdfReader("GeoBase_NHNC1_Data_Model_UML_EN.pdf")
page = reader.pages[3]

parts = []

# Define the coordinates of the ROI (x, y, x1, y1)
# Adjust these coordinates to match your desired ROI
roi_x = 100
roi_y = 100
roi_x1 = 300
roi_y1 = 400

def is_inside_roi(x, y):
    return roi_x <= x <= roi_x1 and roi_y <= y <= roi_y1

def visitor_body(text, cm, tm, fontDict, fontSize):
    x, y = cm[4], tm[5]
    
    if is_inside_roi(x, y):
        parts.append(text)

page.extract_text(visitor_text=visitor_body)
text_body = "".join(parts)

print(text_body)
