# Contributing to SmartPDFInsights

Thank you for considering contributing to SmartPDFInsights! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/smart-pdf-insights.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Install Tesseract OCR: Run `python install_tesseract.py` for instructions

## Development Environment

### Prerequisites

- Python 3.7 or higher
- Tesseract OCR
- PyMuPDF and other dependencies listed in requirements.txt

### Setting Up for Development

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8
```

## Code Style

We follow PEP 8 style guidelines for Python code. Please ensure your code adheres to these standards.

- Use 4 spaces for indentation
- Use meaningful variable and function names
- Add docstrings for all functions, classes, and modules
- Keep line length to a maximum of 88 characters

You can use Black to automatically format your code:

```bash
black .
```

And Flake8 to check for style issues:

```bash
flake8 .
```

## Testing

Write tests for all new features and bug fixes. Run the test suite before submitting a pull request:

```bash
pytest
```

To check test coverage:

```bash
pytest --cov=.
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the requirements.txt if you've added new dependencies
3. Make sure all tests pass
4. Submit a pull request with a clear description of the changes

## Adding New Features

### Heading Extraction Improvements

When improving heading extraction:

1. Add your new extraction method to the `PDFProcessor` class
2. Ensure it works for both regular and scanned PDFs
3. Add appropriate tests
4. Document the approach in comments

### Persona Matching Improvements

When improving persona matching:

1. Modify the `HybridRetriever` class or add new retrieval methods
2. Ensure CPU efficiency is maintained
3. Add appropriate tests
4. Document the approach in comments

### Summarization Improvements

When improving summarization:

1. Modify the `ContextAwareSummarizer` class
2. Ensure model size remains reasonable
3. Add appropriate tests
4. Document the approach in comments

## License

By contributing to SmartPDFInsights, you agree that your contributions will be licensed under the project's MIT License.