# SmartPDFInsights: Enhanced NLP System for PDF Analysis

SmartPDFInsights is an advanced NLP system designed to extract headings, identify relevant sections, and generate persona-specific insights from PDF documents. This implementation focuses on improving accuracy for heading extraction and persona-based relevance matching while maintaining CPU-only operation and reasonable model sizes.

## Features

### Enhanced Heading Extraction (Round 1A)
- Multi-feature heading detection using font attributes, positional information, and text patterns
- Adaptive thresholding based on document statistics
- OCR support for scanned PDFs with image preprocessing
- Hierarchical organization of headings

### Improved Persona Analysis & Relevance Matching (Round 1B)
- Hybrid retrieval combining sparse (TF-IDF) and dense (transformer embeddings) approaches
- Context-aware query expansion for better persona matching
- Position bias and length normalization for smarter scoring
- Two-stage summarization for higher quality insights
- Lightweight model fine-tuning with adapter modules

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-pdf-insights.git
cd smart-pdf-insights

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (required for scanned PDFs)
# On Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
# On Linux: apt-get install tesseract-ocr
# On macOS: brew install tesseract
```

## Usage

### Basic Usage

```bash
python smart_pdf_insights.py --pdf document.pdf --persona "business professional"
```

### Advanced Options

```bash
python smart_pdf_insights.py \
  --pdf document.pdf \
  --persona "researcher in machine learning" \
  --output results.json \
  --model_path ./custom_models
```

### Fine-Tuning the Retriever Model

```bash
python finetune_models.py --data training_data.json --output ./fine_tuned_models
```

The training data should be in the format shown in the `sample_training_data.json` file, with sections and persona-specific relevance mappings.

### Evaluation

```bash
python smart_pdf_insights.py \
  --pdf document.pdf \
  --persona "student" \
  --evaluate ground_truth.json
```

## Components

### PDF Processor (`pdf_processor.py`)
Handles PDF parsing, heading extraction, and OCR for scanned documents.

### Hybrid Retriever (`hybrid_retriever.py`)
Implements the hybrid retrieval system combining TF-IDF and transformer embeddings for improved section matching.

### Context-Aware Summarizer (`context_aware_summarizer.py`)
Provides persona-specific summarization using BART model with quantization for CPU efficiency. The system was updated from T5 to BART to avoid the sentencepiece dependency, making it more compatible with various environments.

### Main System (`smart_pdf_insights.py`)
Integrates all components and provides the main functionality.

## Evaluation Metrics

The system includes built-in evaluation metrics:

- **Heading Extraction**: Precision, Recall, F1 score
- **Relevance Ranking**: Precision@k, Recall@k, Mean Average Precision (MAP)

## Ground Truth Format

For evaluation, provide a JSON file with the following structure:

```json
{
  "headings": [
    {"text": "Introduction", "level": 1},
    {"text": "Methodology", "level": 1},
    {"text": "Data Collection", "level": 2}
  ],
  "personas": {
    "researcher": [
      {"id": "section_2", "heading": "Methodology"},
      {"id": "section_3", "heading": "Data Collection"}
    ],
    "business professional": [
      {"id": "section_5", "heading": "Results"},
      {"id": "section_8", "heading": "Business Impact"}
    ]
  }
}
```

## Performance Considerations

- All models are optimized for CPU usage with quantization
- The system works offline without requiring internet connectivity
- Model sizes are kept reasonable for deployment in constrained environments
- Docker-compatible implementation

## License

MIT