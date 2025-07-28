@echo off
setlocal enabledelayedexpansion

REM Build the Docker image
docker build -t smart-pdf-insights .

REM Run the container with the specified PDF file
REM Usage: run_docker.bat path\to\your\document.pdf [persona]

set PDF_PATH=%~1
set PERSONA=%~2

if "%PERSONA%"=="" (
    set PERSONA=business professional
)

if "%PDF_PATH%"=="" (
    echo Error: PDF path is required
    echo Usage: run_docker.bat path\to\your\document.pdf [persona]
    exit /b 1
)

REM Get absolute path and filename of the PDF file
set ABS_PDF_PATH=%~f1
set PDF_FILENAME=%~nx1

REM Create output directory if it doesn't exist
if not exist "%CD%\output" mkdir "%CD%\output"

REM Run the Docker container
docker run --rm ^
    -v "%ABS_PDF_PATH%:/app/input/%PDF_FILENAME%" ^
    -v "%CD%\output:/app/output" ^
    smart-pdf-insights ^
    --pdf "/app/input/%PDF_FILENAME%" ^
    --persona "%PERSONA%" ^
    --output "/app/output/insights.json"

echo.
echo Results saved to .\output\insights.json