from fpdf import FPDF

def create_sample_pdf(output_file="sample.pdf"):
    """Create a sample PDF file with headings and content for testing"""
    pdf = FPDF()
    
    # Add first page
    pdf.add_page()
    
    # Set font for title
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "Sample Document for SmartPDFInsights", 0, 1, "C")
    
    # Introduction section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "1. Introduction", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "This is a sample document created for testing the SmartPDFInsights system. It contains various headings and content sections to evaluate the heading extraction and persona matching capabilities.")
    
    # Background section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 15, "1.1 Background", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "The field of Natural Language Processing has evolved significantly over the past decades. From simple rule-based systems to complex neural networks, the advancements have enabled solutions to previously unsolvable problems. This section provides historical context and foundational knowledge necessary for understanding current approaches.")
    
    # Add second page
    pdf.add_page()
    
    # Problem Statement section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 15, "1.2 Problem Statement", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "Despite advances in NLP, several challenges remain in PDF analysis. These include heading extraction accuracy, relevance matching for different personas, and generating meaningful insights. This document addresses these challenges and proposes methodologies to overcome them in practical applications.")
    
    # Methodology section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "2. Methodology", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "Our approach combines traditional statistical methods with deep learning techniques. We employ a multi-stage pipeline that includes heading extraction, section identification, persona matching, and insight generation. Each stage is designed to address specific challenges identified in the problem statement.")
    
    # Data Collection section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 15, "2.1 Data Collection", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "The dataset used in this study consists of various PDF documents collected from academic, business, and technical sources. Each document contains different heading styles, layouts, and content types. The data collection process involved rigorous quality checks to ensure diversity and representativeness.")
    
    # Add third page
    pdf.add_page()
    
    # Analysis Techniques section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 15, "2.2 Analysis Techniques", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "We employed several analytical techniques including PyMuPDF for structural analysis, OCR for scanned documents, hybrid retrieval combining TF-IDF and transformer embeddings, and context-aware summarization. Additionally, we used evaluation metrics to quantify performance improvements.")
    
    # Results section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "3. Results", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "Our experiments demonstrate significant improvements over baseline methods. The proposed approach achieved higher accuracy in heading extraction and better relevance matching for different personas. The results were consistent across multiple evaluation metrics including precision, recall, and F1 score.")
    
    # Key Findings section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 15, "3.1 Key Findings", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "The key findings from our study include: (1) multi-feature heading detection significantly improves extraction accuracy, (2) hybrid retrieval methods consistently outperform single-approach methods, and (3) context-aware summarization produces more relevant insights for different personas.")
    
    # Add fourth page
    pdf.add_page()
    
    # Discussion section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "4. Discussion", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "The results of this study have several implications for both research and practice. From a theoretical perspective, our findings demonstrate the effectiveness of combining multiple approaches for PDF analysis. From a practical standpoint, the proposed methodology offers a blueprint for implementing NLP solutions for document analysis.")
    
    # Business Implications section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 15, "4.1 Business Implications", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "The business implications of our work are substantial. Organizations can leverage the proposed approach to improve document processing, knowledge extraction, and information retrieval. This can lead to significant time savings and better decision-making based on document insights.")
    
    # Conclusion section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "5. Conclusion", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "In conclusion, this document presented a novel approach to PDF analysis that balances accuracy, efficiency, and practical applicability. The empirical results demonstrate the effectiveness of the proposed methodology across various metrics. We believe this work contributes significantly to both the theoretical understanding and practical application of NLP for document analysis.")
    
    # Save the PDF
    pdf.output(output_file)
    print(f"Sample PDF created: {output_file}")

if __name__ == "__main__":
    create_sample_pdf()