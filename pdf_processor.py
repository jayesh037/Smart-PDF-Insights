import fitz  # PyMuPDF
import numpy as np
import cv2
from PIL import Image
import pytesseract

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_headings(self, pdf_path):
        """Enhanced heading extraction using multiple features"""
        doc = fitz.open(pdf_path)
        
        # First try to extract the built-in outline/table of contents
        outline = self.extract_pdf_outline(doc)
        if outline and len(outline) > 0:
            return outline
        
        # If no built-in outline, use heuristic methods
        # Check if it's a scanned PDF
        if self.is_scanned_pdf(doc):
            return self.extract_headings_from_scanned_pdf(doc)
        else:
            return self.extract_headings_improved(doc)
    
    def extract_pdf_outline(self, doc):
        """Extract the built-in outline/table of contents from the PDF
        
        Args:
            doc: The fitz document object
            
        Returns:
            List of headings from the PDF's built-in outline, or empty list if none exists
        """
        try:
            # Get the table of contents from the PDF
            toc = doc.get_toc()
            
            # If no TOC exists, return empty list
            if not toc:
                return []
            
            # Convert TOC to our heading format
            headings = []
            for item in toc:
                level, title, page = item[:3]
                headings.append({
                    "text": title,
                    "page": page,
                    "level": f"H{level}" if level <= 6 else "H6"
                })
            
            return headings
        except Exception as e:
            print(f"Error extracting PDF outline: {e}")
            return []
    
    def extract_headings_improved(self, doc):
        """Extract headings using font attributes and positional information"""
        headings = []
        
        # Track document statistics for adaptive thresholding
        font_sizes = []
        font_weights = []
        
        # First pass: collect statistics
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_sizes.append(span["size"])
                            font_weights.append(span["flags"] & 2)  # Check bold flag
        
        # Calculate adaptive thresholds
        if font_sizes:
            mean_size = sum(font_sizes) / len(font_sizes)
            size_threshold = mean_size * 1.2  # 20% larger than average
        else:
            size_threshold = 12  # Default fallback
        
        # Second pass: extract headings using multiple features
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        is_heading = False
                        line_size = 0
                        is_bold = False
                        
                        # Analyze spans in the line
                        for span in line["spans"]:
                            line_text += span["text"]
                            line_size = max(line_size, span["size"])
                            if span["flags"] & 2:  # Check bold flag
                                is_bold = True
                        
                        # Apply multiple criteria for heading detection
                        if (line_size > size_threshold or 
                            (is_bold and line_size > mean_size) or
                            (len(line_text.strip()) < 100 and line_text.strip().endswith(":")) or
                            any(line_text.strip().startswith(p) for p in ["Chapter", "Section", "Part"])):
                            
                            # Additional validation: avoid false positives
                            if not any(line_text.strip().startswith(p) for p in ["http", "www", "Figure", "Table"]):
                                headings.append({
                                    "text": line_text.strip(),
                                    "page": page_num + 1,
                                    "size": line_size,
                                    "bold": is_bold,
                                    "level": self.determine_heading_level(line_size, is_bold, font_sizes)
                                })
        
        return headings
    
    def determine_heading_level(self, size, is_bold, font_sizes):
        """Determine heading level based on font size and style"""
        # Sort font sizes in descending order
        sorted_sizes = sorted(set(font_sizes), reverse=True)
        
        # Determine level based on font size ranking
        if size in sorted_sizes:
            level = sorted_sizes.index(size) + 1
            # Adjust level if bold (might be one level higher in hierarchy)
            if is_bold and level > 1:
                level -= 1
            return min(level, 6)  # Cap at h6
        return 6  # Default to lowest heading level
    
    def is_scanned_pdf(self, doc):
        """Detect if PDF is likely scanned by checking image to text ratio"""
        image_area = 0
        page_area = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_area += page.rect.width * page.rect.height
            
            for img in page.get_images(full=True):
                xref = img[0]
                image = doc.extract_image(xref)
                image_area += image["width"] * image["height"]
        
        # If images cover more than 80% of the document, likely scanned
        return image_area / page_area > 0.8 if page_area else False
    
    def extract_headings_from_scanned_pdf(self, doc):
        """Extract headings from scanned PDF using OCR"""
        headings = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution for OCR
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to numpy array for OpenCV processing
            img_np = np.array(img)
            
            # Enhance image for better OCR
            img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            img_gray = cv2.adaptiveThreshold(
                img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # OCR with layout analysis
            custom_config = r'--oem 3 --psm 3'  # Page segmentation mode 3: fully automatic page segmentation
            ocr_data = pytesseract.image_to_data(img_gray, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Process OCR results to identify potential headings
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if text and ocr_data['conf'][i] > 70:  # Confidence threshold
                    # Heading heuristics for OCR: shorter lines with larger font
                    if (len(text) < 100 and ocr_data['height'][i] > 1.3 * np.mean(ocr_data['height'])):
                        headings.append({
                            "text": text,
                            "page": page_num + 1,
                            "confidence": ocr_data['conf'][i],
                            "level": self.estimate_heading_level_from_ocr(ocr_data, i)
                        })
        
        return headings
    
    def estimate_heading_level_from_ocr(self, ocr_data, index):
        """Estimate heading level from OCR data"""
        # Get height of current text element
        height = ocr_data['height'][index]
        
        # Get all heights and sort them
        all_heights = [h for h in ocr_data['height'] if h > 0]
        all_heights.sort(reverse=True)
        
        # Determine level based on height ranking
        if height in all_heights:
            level = all_heights.index(height) + 1
            return min(level, 6)  # Cap at h6
        return 6  # Default to lowest heading level