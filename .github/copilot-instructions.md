<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# CPU Data Processor - Copilot Instructions

This is a Python application for processing CPU product pages with the following functionality:

## Project Overview
- Web scraping CPU product pages
- Converting HTML to PDF using wkhtmltopdf
- Extracting text from PDF files
- Integration with Ollama LLM API (mistral-small3.2:24b model)
- JSON parsing and data extraction
- Excel file management using pandas

## Key Components
- `cpu_processor.py`: Main application with CPUDataProcessor class
- Uses requests, BeautifulSoup, selenium, pdfkit, PyPDF2, pandas, openpyxl, ollama
- Ollama API endpoint: http://192.168.101.66:11434
- Output: cpu_data.xlsx with structured CPU information

## Code Style Guidelines
- Use type hints where appropriate
- Include comprehensive error handling
- Add logging for debugging and monitoring
- Follow PEP 8 conventions
- Use docstrings for functions and classes

## Dependencies
- Ensure all external dependencies are properly handled
- Include system requirements (wkhtmltopdf) in documentation
- Handle network timeouts and API failures gracefully
