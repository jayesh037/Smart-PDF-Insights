import fitz  # PyMuPDF

def create_pdf_with_outline():
    # Create a new PDF document
    doc = fitz.open()
    
    # Add pages
    for i in range(5):
        page = doc.new_page(width=595, height=842)  # A4 size
        
        # Add some text to each page
        text = f"Page {i+1}"
        page.insert_text((50, 50), text, fontsize=12)
        
        # Add headings
        if i == 0:
            page.insert_text((50, 100), "Introduction", fontsize=16)
            page.insert_text((50, 150), "This is the introduction section.", fontsize=12)
        elif i == 1:
            page.insert_text((50, 100), "Background and Context", fontsize=16)
            page.insert_text((50, 150), "This is the background section.", fontsize=12)
        elif i == 2:
            page.insert_text((50, 100), "Methodology", fontsize=16)
            page.insert_text((50, 150), "This is the methodology section.", fontsize=12)
        elif i == 3:
            page.insert_text((50, 100), "Results", fontsize=16)
            page.insert_text((50, 150), "This is the results section.", fontsize=12)
            page.insert_text((50, 200), "Key Findings", fontsize=14)
            page.insert_text((50, 250), "Statistical Analysis", fontsize=12)
        elif i == 4:
            page.insert_text((50, 100), "Conclusion", fontsize=16)
            page.insert_text((50, 150), "This is the conclusion section.", fontsize=12)
    
    # Create the outline/table of contents
    toc = [
        [1, "Introduction", 1],
        [2, "Background and Context", 2],
        [1, "Methodology", 3],
        [1, "Results", 4],
        [2, "Key Findings", 4],
        [3, "Statistical Analysis", 4],
        [1, "Conclusion", 5]
    ]
    
    # Set the outline
    doc.set_toc(toc)
    
    # Save the PDF
    doc.save("test_pdf_with_outline.pdf")
    print("Created test_pdf_with_outline.pdf with built-in outline/table of contents")

if __name__ == "__main__":
    create_pdf_with_outline()