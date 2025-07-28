import os
import argparse
import json
from smart_pdf_insights import SmartPDFInsights

def test_heading_extraction(pdf_path):
    """Test the heading extraction functionality
    
    Args:
        pdf_path: Path to the PDF file
    """
    print("\n=== Testing Heading Extraction ===\n")
    
    # Initialize system
    system = SmartPDFInsights()
    
    # Process PDF
    print(f"Processing PDF: {pdf_path}")
    result = system.process_pdf(pdf_path)
    
    # Print extracted headings
    print(f"\nExtracted {len(result['headings'])} headings:")
    for i, heading in enumerate(result['headings'][:10]):  # Show first 10 headings
        print(f"  {i+1}. {heading['text']} (Level: {heading.get('level', 'N/A')}, Page: {heading.get('page', 'N/A')})")
    
    if len(result['headings']) > 10:
        print(f"  ... and {len(result['headings']) - 10} more")
    
    # Print document structure
    print("\nDocument Structure:")
    _print_structure(result['structure'])

def _print_structure(nodes, level=0):
    """Helper function to print document structure
    
    Args:
        nodes: List of structure nodes
        level: Current indentation level
    """
    for node in nodes:
        print(f"{'  ' * level}• {node['text']} (Page: {node.get('page', 'N/A')})")
        if node.get('children'):
            _print_structure(node['children'], level + 1)

def test_persona_matching(pdf_path, persona):
    """Test the persona matching functionality
    
    Args:
        pdf_path: Path to the PDF file
        persona: Description of the target persona
    """
    print(f"\n=== Testing Persona Matching for '{persona}' ===\n")
    
    # Initialize system
    system = SmartPDFInsights()
    
    # Extract sections
    print("Extracting sections...")
    sections = system.extract_sections(pdf_path)
    print(f"Extracted {len(sections)} sections")
    
    # Match sections to persona
    print(f"\nMatching sections to persona: {persona}")
    matched_sections = system.match_sections_to_persona(sections, persona, top_k=5)
    
    # Print matched sections
    print(f"\nTop {len(matched_sections)} sections for {persona}:")
    for i, section in enumerate(matched_sections):
        print(f"  {i+1}. {section['heading']} (Page: {section['page']}, Score: {section.get('score', 0.0):.4f})")
        print(f"     Sparse Score: {section.get('sparse_score', 0.0):.4f}, Dense Score: {section.get('dense_score', 0.0):.4f}")
        print(f"     Content Preview: {section['content'][:100]}...")
        print()

def test_insight_generation(pdf_path, persona):
    """Test the insight generation functionality
    
    Args:
        pdf_path: Path to the PDF file
        persona: Description of the target persona
    """
    print(f"\n=== Testing Insight Generation for '{persona}' ===\n")
    
    # Initialize system
    system = SmartPDFInsights()
    
    # Extract sections
    print("Extracting sections...")
    sections = system.extract_sections(pdf_path)
    
    # Match sections to persona
    print(f"Matching sections to persona: {persona}")
    matched_sections = system.match_sections_to_persona(sections, persona, top_k=3)
    
    # Generate insights
    print("\nGenerating insights...")
    insights = system.generate_insights(matched_sections, persona)
    
    # Print insights
    print(f"\nGenerated {len(insights)} insights for {persona}:")
    for i, insight in enumerate(insights):
        print(f"  {i+1}. {insight['heading']} (Page: {insight['page']}, Relevance: {insight.get('relevance_score', 0.0):.4f})")
        print(f"     Summary: {insight['summary']}")
        print()

def main():
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description="Test SmartPDFInsights functionality")
    parser.add_argument("--pdf", type=str, required=True, help="Path to PDF file")
    parser.add_argument("--persona", type=str, default="business professional", 
                        help="Target persona for testing")
    parser.add_argument("--test", type=str, choices=['all', 'headings', 'matching', 'insights'],
                        default='all', help="Test to run")
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file '{args.pdf}' not found")
        return
    
    # Run selected tests
    if args.test in ['all', 'headings']:
        test_heading_extraction(args.pdf)
    
    if args.test in ['all', 'matching']:
        test_persona_matching(args.pdf, args.persona)
    
    if args.test in ['all', 'insights']:
        test_insight_generation(args.pdf, args.persona)

if __name__ == "__main__":
    main()