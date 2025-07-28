#!/usr/bin/env python
"""
Demo script for SmartPDFInsights

This script demonstrates how to use the SmartPDFInsights system with a sample PDF.
It performs heading extraction, persona matching, and insight generation.

Usage:
    python demo.py --pdf sample.pdf
"""

import os
import argparse
import json
from smart_pdf_insights import SmartPDFInsights

def run_demo(pdf_path):
    """Run a complete demonstration of the SmartPDFInsights system
    
    Args:
        pdf_path: Path to the PDF file
    """
    print("\n===== SmartPDFInsights Demo =====\n")
    print(f"Processing PDF: {pdf_path}\n")
    
    # Initialize system
    system = SmartPDFInsights()
    
    # Step 1: Extract headings
    print("Step 1: Extracting headings and document structure...")
    result = system.process_pdf(pdf_path)
    headings = result["headings"]
    
    print(f"  Extracted {len(headings)} headings")
    print("  Sample headings:")
    for i, heading in enumerate(headings[:3]):  # Show first 3 headings
        print(f"    - {heading['text']} (Level: {heading.get('level', 'N/A')}, Page: {heading.get('page', 'N/A')})")
    if len(headings) > 3:
        print(f"    - ... and {len(headings) - 3} more")
    print()
    
    # Step 2: Extract sections
    print("Step 2: Extracting sections...")
    sections = system.extract_sections(pdf_path)
    
    print(f"  Extracted {len(sections)} sections")
    print("  Sample sections:")
    for i, section in enumerate(sections[:3]):  # Show first 3 sections
        content_preview = section['content'][:100] + "..." if len(section['content']) > 100 else section['content']
        print(f"    - {section['heading']} (Page: {section['page']})")
        print(f"      Preview: {content_preview}")
    if len(sections) > 3:
        print(f"    - ... and {len(sections) - 3} more")
    print()
    
    # Step 3: Demonstrate persona matching for different personas
    personas = ["researcher", "business professional", "student"]
    
    for persona in personas:
        print(f"Step 3.{personas.index(persona)+1}: Matching sections for '{persona}' persona...")
        matched_sections = system.match_sections_to_persona(sections, persona, top_k=3)
        
        print(f"  Top {len(matched_sections)} sections for {persona}:")
        for i, section in enumerate(matched_sections):
            print(f"    {i+1}. {section['heading']} (Score: {section.get('score', 0.0):.4f})")
        print()
        
        # Step 4: Generate insights for each persona
        print(f"Step 4.{personas.index(persona)+1}: Generating insights for '{persona}' persona...")
        insights = system.generate_insights(matched_sections, persona)
        
        print(f"  Generated {len(insights)} insights:")
        for i, insight in enumerate(insights):
            print(f"    {i+1}. {insight['heading']}")
            print(f"       Summary: {insight['summary']}")
            print()
    
    # Save results to file
    output_file = "demo_results.json"
    output = {
        "pdf": pdf_path,
        "headings": headings,
        "personas": {}
    }
    
    for persona in personas:
        matched_sections = system.match_sections_to_persona(sections, persona, top_k=3)
        insights = system.generate_insights(matched_sections, persona)
        
        output["personas"][persona] = {
            "matched_sections": [{
                "heading": s["heading"],
                "page": s["page"],
                "score": s.get("score", 0.0)
            } for s in matched_sections],
            "insights": insights
        }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nDemo results saved to {output_file}")
    print("\n===== Demo Complete =====\n")

def main():
    """Main function to run the demo"""
    parser = argparse.ArgumentParser(description="SmartPDFInsights Demo")
    parser.add_argument("--pdf", type=str, required=True, help="Path to PDF file")
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not os.path.exists(args.pdf):
        print(f"Error: PDF file '{args.pdf}' not found")
        return
    
    # Run the demo
    run_demo(args.pdf)

if __name__ == "__main__":
    main()