#!/usr/bin/env python
"""
Tesseract OCR Installation Helper

This script helps users install Tesseract OCR, which is required for processing scanned PDFs.
It provides instructions for different operating systems and checks if Tesseract is already installed.
"""

import os
import sys
import subprocess
import platform

def check_tesseract_installed():
    """Check if Tesseract OCR is already installed
    
    Returns:
        bool: True if installed, False otherwise
    """
    try:
        # Try to run tesseract command
        result = subprocess.run(
            ["tesseract", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_install_instructions():
    """Get installation instructions based on operating system
    
    Returns:
        str: Installation instructions
    """
    system = platform.system().lower()
    
    if system == "windows":
        return """
Windows Installation Instructions:

1. Download the Tesseract installer from:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Run the installer and follow the installation wizard.

3. Add Tesseract to your PATH environment variable:
   - Right-click on 'This PC' or 'My Computer' and select 'Properties'
   - Click on 'Advanced system settings'
   - Click on 'Environment Variables'
   - Under 'System variables', find and select 'Path', then click 'Edit'
   - Click 'New' and add the Tesseract installation directory (e.g., C:\Program Files\Tesseract-OCR)
   - Click 'OK' on all dialogs to save changes

4. Restart your command prompt or IDE for the changes to take effect.
"""
    
    elif system == "darwin":  # macOS
        return """
macOS Installation Instructions:

1. Install Homebrew if you don't have it already:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Install Tesseract using Homebrew:
   brew install tesseract

3. Verify installation:
   tesseract --version
"""
    
    elif system == "linux":
        return """
Linux Installation Instructions:

1. Install Tesseract using your package manager:

   For Ubuntu/Debian:
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   sudo apt-get install libtesseract-dev

   For Fedora:
   sudo dnf install tesseract
   sudo dnf install tesseract-devel

   For Arch Linux:
   sudo pacman -S tesseract
   sudo pacman -S tesseract-data-eng

2. Verify installation:
   tesseract --version
"""
    
    else:
        return "Unsupported operating system. Please install Tesseract OCR manually."

def main():
    """Main function to check Tesseract installation and provide instructions"""
    print("\n===== Tesseract OCR Installation Helper =====\n")
    
    # Check if Tesseract is already installed
    if check_tesseract_installed():
        print("✅ Tesseract OCR is already installed on your system.")
        print("You're ready to use SmartPDFInsights with scanned PDFs!")
        return
    
    # Tesseract is not installed, provide instructions
    print("❌ Tesseract OCR is not installed or not in your PATH.")
    print("\nTesseract OCR is required for processing scanned PDFs.")
    print("Please follow the installation instructions below:\n")
    
    instructions = get_install_instructions()
    print(instructions)
    
    print("\nAfter installation, run this script again to verify.")
    print("\n===== End of Installation Helper =====\n")

if __name__ == "__main__":
    main()