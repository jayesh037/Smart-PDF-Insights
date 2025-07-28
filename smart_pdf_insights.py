import os
import argparse
import json
from typing import List, Dict, Optional, Union, Tuple

from pdf_processor import PDFProcessor
from hybrid_retriever import HybridRetriever, AdapterFineTuner
from context_aware_summarizer import ContextAwareSummarizer, EvaluationMetrics

class SmartPDFInsights:
    """Main class for the SmartPDFInsights system integrating all components"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the SmartPDFInsights system
        
        Args:
            model_path: Optional path to pre-trained models
        """
        # Initialize components
        self.pdf_processor = PDFProcessor()
        
        # Check if fine-tuned model exists
        fine_tuned_model_path = './fine_tuned_models/retriever'
        if os.path.exists(fine_tuned_model_path):
            print(f"Using fine-tuned retriever model from {fine_tuned_model_path}")
            self.retriever = HybridRetriever(model_name=fine_tuned_model_path, sparse_weight=0.3)
        else:
            # Use smaller models for CPU efficiency
            print("Using default retriever model")
            self.retriever = HybridRetriever(model_name='all-MiniLM-L6-v2', sparse_weight=0.3)
        self.summarizer = ContextAwareSummarizer(model_name='facebook/bart-base')
        
        # Load custom models if provided
        if model_path and os.path.exists(model_path):
            self._load_custom_models(model_path)
    
    def _load_custom_models(self, model_path: str):
        """Load custom fine-tuned models if available
        
        Args:
            model_path: Path to directory containing models
        """
        # Check for custom retriever model
        retriever_path = os.path.join(model_path, 'retriever')
        if os.path.exists(retriever_path):
            try:
                self.retriever.model = self.retriever.model.load(retriever_path)
                print(f"Loaded custom retriever model from {retriever_path}")
            except Exception as e:
                print(f"Failed to load custom retriever model: {e}")
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a PDF document to extract headings and structure
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted headings and document structure
        """
        # Extract headings with improved method
        headings = self.pdf_processor.extract_headings(pdf_path)
        
        # Extract PDF content and properties
        import fitz
        doc = fitz.open(pdf_path)
        content = ""
        properties = {
            "page_count": len(doc),
            "metadata": doc.metadata,
            "is_encrypted": doc.is_encrypted,
            "permissions": doc.permissions
        }
        
        # Extract text from each page
        for page in doc:
            content += page.get_text() + "\n\n"
        
        # Check if headings were extracted from the built-in outline
        # (headings from built-in outline will have 'level' as 'H1', 'H2', etc.)
        if headings and all(isinstance(h.get('level'), str) and h.get('level', '').startswith('H') for h in headings):
            # Return the exact outline from the PDF with content and properties
            return {
                "title": os.path.basename(pdf_path),
                "outline": headings,
                "content": content,
                "properties": properties
            }
        
        # For headings extracted using heuristic methods, organize into a hierarchical structure
        document_structure = self._organize_headings(headings)
        
        # Return in the structured format with content and properties
        return {
            "headings": headings,
            "structure": document_structure,
            "content": content,
            "properties": properties
        }
    
    def _organize_headings(self, headings: List[Dict]) -> List[Dict]:
        """Organize headings into a hierarchical structure
        
        Args:
            headings: List of extracted headings
            
        Returns:
            Hierarchical structure of headings
        """
        # Sort headings by page and position
        sorted_headings = sorted(headings, key=lambda h: (h.get("page", 0), h.get("y", 0)))
        
        # Create hierarchical structure
        root = []
        stack = [(0, root)]  # (level, children_list)
        
        for heading in sorted_headings:
            level = heading.get("level", 6)  # Default to lowest level if not specified
            node = {"text": heading.get("text", ""), "children": [], "page": heading.get("page", 0)}
            
            # Pop from stack until we find a parent level
            while stack and stack[-1][0] >= level:
                stack.pop()
            
            # Add to parent's children
            if stack:
                stack[-1][1].append(node)
            else:
                root.append(node)
            
            # Push current level to stack
            stack.append((level, node["children"]))
        
        return root
    
    def extract_sections(self, pdf_path: str) -> List[Dict]:
        """Extract sections from PDF based on heading structure
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of sections with text content
        """
        # First extract headings
        result = self.process_pdf(pdf_path)
        
        # Handle both outline format and headings format
        if "outline" in result:
            headings = result["outline"]
        else:
            headings = result["headings"]
        
        # Open PDF for text extraction
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        
        # Extract text from each page
        page_texts = [page.get_text() for page in doc]
        
        # Sort headings by page and position
        sorted_headings = sorted(headings, key=lambda h: (h.get("page", 0), h.get("y", 0)))
        
        # Extract sections between headings
        sections = []
        for i in range(len(sorted_headings)):
            current = sorted_headings[i]
            
            # Determine section end (next heading or end of document)
            if i < len(sorted_headings) - 1:
                next_heading = sorted_headings[i + 1]
                end_page = next_heading["page"] - 1
                end_pos = 0
            else:
                end_page = len(page_texts) - 1
                end_pos = len(page_texts[-1])
            
            # Extract text between current heading and next heading
            section_text = ""
            
            # Add current heading text
            section_text += current["text"] + "\n\n"
            
            # Add content after heading on the same page
            current_page = current["page"] - 1  # Convert to 0-indexed
            if current_page <= end_page:
                page_text = page_texts[current_page]
                # Find position of heading in page text
                heading_pos = page_text.find(current["text"])
                if heading_pos >= 0:
                    section_text += page_text[heading_pos + len(current["text"]):] + "\n"
            
            # Add content from subsequent pages
            for p in range(current_page + 1, end_page + 1):
                if p < len(page_texts):
                    section_text += page_texts[p] + "\n"
            
            sections.append({
                "heading": current["text"],
                "level": current.get("level", 6),
                "page": current["page"],
                "content": section_text.strip(),
                "id": f"section_{i}"
            })
        
        return sections
    
    def match_sections_to_persona(self, sections: List[Dict], persona: str, top_k: int = 5) -> List[Dict]:
        """Match sections to a persona using hybrid retrieval
        
        Args:
            sections: List of extracted sections
            persona: Description of the target persona
            top_k: Number of top sections to return
            
        Returns:
            List of top sections relevant to the persona
        """
        # Extract section texts and metadata
        texts = [section["content"] for section in sections]
        metadata = [{
            "heading": section["heading"],
            "level": section.get("level", 6),
            "page": section["page"],
            "id": section.get("id", f"section_{i}")
        } for i, section in enumerate(sections)]
        
        # Index the corpus
        self.retriever.index_corpus(texts, metadata)
        
        # Retrieve top sections for the persona
        results = self.retriever.retrieve(persona, top_k=top_k, expand=True)
        
        # Combine results with original sections
        matched_sections = []
        for result in results:
            section_id = result["metadata"]["id"]
            section_idx = int(section_id.split("_")[1]) if "_" in section_id else 0
            
            if section_idx < len(sections):
                section = sections[section_idx].copy()
                section["score"] = result["score"]
                section["sparse_score"] = result["sparse_score"]
                section["dense_score"] = result["dense_score"]
                matched_sections.append(section)
        
        return matched_sections
    
    def generate_insights(self, sections: List[Dict], persona: str) -> List[Dict]:
        """Generate insights from matched sections for a specific persona
        
        Args:
            sections: List of sections matched to persona
            persona: Description of the target persona
            
        Returns:
            List of insights with summaries
        """
        insights = []
        
        for section in sections:
            # Use two-stage summarization for better quality
            summary = self.summarizer.generate_two_stage_summary(
                section["content"], persona, max_length=150
            )
            
            insights.append({
                "heading": section["heading"],
                "page": section["page"],
                "summary": summary,
                "relevance_score": section.get("score", 0.0)
            })
        
        return insights
    
    def evaluate(self, pdf_path: str, ground_truth_file: str) -> Dict:
        """Evaluate system performance against ground truth
        
        Args:
            pdf_path: Path to the PDF file
            ground_truth_file: Path to ground truth JSON file
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Load ground truth data
        with open(ground_truth_file, 'r') as f:
            ground_truth = json.load(f)
        
        # Process PDF
        result = self.process_pdf(pdf_path)
        headings = result["headings"]
        
        # Extract sections
        sections = self.extract_sections(pdf_path)
        
        # Evaluate heading extraction
        heading_metrics = EvaluationMetrics.evaluate_heading_extraction(
            headings, ground_truth.get("headings", [])
        )
        
        # Evaluate section matching for each persona
        persona_metrics = {}
        for persona, gt_sections in ground_truth.get("personas", {}).items():
            # Match sections to persona
            matched_sections = self.match_sections_to_persona(sections, persona)
            
            # Evaluate relevance ranking
            relevance_metrics = EvaluationMetrics.evaluate_relevance_ranking(
                matched_sections, gt_sections
            )
            
            persona_metrics[persona] = relevance_metrics
        
        return {
            "heading_extraction": heading_metrics,
            "persona_matching": persona_metrics
        }


def main():
    """Main function to run the SmartPDFInsights system"""
    parser = argparse.ArgumentParser(description="SmartPDFInsights: NLP-powered PDF analysis")
    parser.add_argument("--pdf", type=str, required=True, help="Path to PDF file")
    parser.add_argument("--persona", type=str, default="general reader", 
                        help="Target persona for insights")
    parser.add_argument("--output", type=str, default="insights.json", 
                        help="Output file for results")
    parser.add_argument("--evaluate", type=str, help="Path to ground truth file for evaluation")
    parser.add_argument("--model_path", type=str, help="Path to custom models")
    
    args = parser.parse_args()
    
    # Initialize system
    system = SmartPDFInsights(model_path=args.model_path)
    
    # Process PDF
    print(f"Processing PDF: {args.pdf}")
    result = system.process_pdf(args.pdf)
    
    # Extract sections
    print("Extracting sections...")
    sections = system.extract_sections(args.pdf)
    
    # Match sections to persona
    print(f"Matching sections to persona: {args.persona}")
    matched_sections = system.match_sections_to_persona(sections, args.persona)
    
    # Generate insights
    print("Generating insights...")
    insights = system.generate_insights(matched_sections, args.persona)
    
    # Save results
    if "outline" in result:
        # If result contains the exact outline from PDF, use that format
        # Wrap the result in an array to match the requested format
        output = [result]
    else:
        # Use the standard format with headings, structure, matched sections, insights, content and properties
        output = {
            "pdf": args.pdf,
            "persona": args.persona,
            "headings": result["headings"],
            "structure": result["structure"],
            "content": result["content"],
            "properties": result["properties"],
            "matched_sections": [{
                "heading": s["heading"],
                "page": s["page"],
                "score": s.get("score", 0.0)
            } for s in matched_sections],
            "insights": insights
        }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Results saved to {args.output}")
    
    # Run evaluation if ground truth provided
    if args.evaluate:
        print(f"Evaluating against ground truth: {args.evaluate}")
        metrics = system.evaluate(args.pdf, args.evaluate)
        
        # Print evaluation results
        print("\nEvaluation Results:")
        print("Heading Extraction:")
        print(f"  Precision: {metrics['heading_extraction']['precision']:.4f}")
        print(f"  Recall: {metrics['heading_extraction']['recall']:.4f}")
        print(f"  F1: {metrics['heading_extraction']['f1']:.4f}")
        
        print("\nPersona Matching:")
        for persona, results in metrics["persona_matching"].items():
            print(f"  {persona}:")
            for metric, value in results.items():
                print(f"    {metric}: {value:.4f}")


if __name__ == "__main__":
    main()