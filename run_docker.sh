#!/bin/bash

# Build the Docker image
docker build -t smart-pdf-insights .

# Run the container with the specified PDF file
# Usage: ./run_docker.sh path/to/your/document.pdf [persona]

PDF_PATH="$1"
PERSONA="${2:-business professional}"

if [ -z "$PDF_PATH" ]; then
    echo "Error: PDF path is required"
    echo "Usage: ./run_docker.sh path/to/your/document.pdf [persona]"
    exit 1
fi

# Get absolute path of the PDF file
ABS_PDF_PATH=$(realpath "$PDF_PATH")
PDF_FILENAME=$(basename "$PDF_PATH")

# Run the Docker container
docker run --rm \
    -v "$ABS_PDF_PATH:/app/input/$PDF_FILENAME" \
    -v "$(pwd)/output:/app/output" \
    smart-pdf-insights \
    --pdf "/app/input/$PDF_FILENAME" \
    --persona "$PERSONA" \
    --output "/app/output/insights.json"

echo "\nResults saved to ./output/insights.json"