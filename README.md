# CPU Data Processor

A Python application that processes CPU product pages by converting them to PDF and sending them directly to an Ollama LLM for structured data extraction.

## 🚀 Features

- **Web Page to PDF Conversion**: Convert CPU product pages to PDF format
- **Direct PDF Processing**: Send PDFs directly to Ollama without text extraction
- **LLM Integration**: Uses Ollama API with mistral-small3.2:24b model
- **Excel Data Management**: Save and update CPU data in Excel format
- **Interactive Mode**: Easy-to-use command-line interface
- **Error Handling**: Comprehensive error handling and logging
- **Selenium Support**: Optional Selenium for dynamic content rendering

## 📋 Requirements

### System Dependencies
- **wkhtmltopdf**: Required for PDF conversion
  ```bash
  # Ubuntu/Debian
  sudo apt-get install wkhtmltopdf
  
  # CentOS/RHEL
  sudo yum install wkhtmltopdf
  
  # macOS
  brew install wkhtmltopdf
  ```

- **Google Chrome**: Required for Selenium (optional)
  ```bash
  # Ubuntu/Debian
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
  sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
  sudo apt-get update
  sudo apt-get install google-chrome-stable
  ```

### Python Dependencies
Install Python dependencies using pip:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Ollama Setup
- **Server URL**: `http://192.168.101.66:11434`
- **Model**: `qwen2.5vl:latest` (Vision-Language model for document processing)

Make sure your Ollama server is running and the model is available:
```bash
# Check if model is available
curl http://192.168.101.66:11434/api/tags

# Pull the model if not available
ollama pull qwen2.5vl:latest
```

## 🎯 Usage

### Interactive Mode
Run the application in interactive mode:
```bash
python cpu_processor.py
```

The application will prompt you to:
1. Enter a CPU product page URL
2. Choose whether to use Selenium for dynamic content
3. Process the URL and save data to Excel

### Example URLs
Test with CPU product pages from:
- Intel official website
- AMD official website
- Retailer websites (Newegg, Amazon, etc.)
- Tech review sites

## 📊 Output Format

The application extracts and saves the following information to `CPU-DATA.xlsx`:

```json
{
    "cpu_id": "unique identifier or model number",
    "brand": "manufacturer name (Intel, AMD, etc.)",
    "model": "specific model name",
    "series": "product series",
    "cores": "number of cores",
    "threads": "number of threads",
    "base_clock": "base clock speed",
    "boost_clock": "maximum boost clock speed",
    "cache": "cache information",
    "tdp": "thermal design power",
    "socket": "socket type",
    "architecture": "CPU architecture",
    "process_node": "manufacturing process",
    "launch_date": "launch date",
    "price": "current price if available",
    "specifications": "additional key specifications",
    "url": "source URL"
}
```

## 🔧 Advanced Usage

### Custom Configuration
You can modify the processor settings:
```python
from cpu_processor import CPUDataProcessor

# Custom configuration
processor = CPUDataProcessor(
    ollama_url="http://your-ollama-server:11434",
    model_name="your-model-name",
    excel_file="custom_output.xlsx"
)

# Process a single URL
cpu_data = processor.process_url("https://example.com/cpu-page")
```

### Batch Processing
For processing multiple URLs:
```python
urls = [
    "https://example1.com/cpu1",
    "https://example2.com/cpu2",
    # ... more URLs
]

for url in urls:
    try:
        processor.process_url(url)
        print(f"✅ Processed: {url}")
    except Exception as e:
        print(f"❌ Failed: {url} - {e}")
```

## 📁 Project Structure

```
cpu_processor/
├── cpu_processor.py     # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── CPU-DATA.xlsx       # Output Excel file (generated)
```

## 🐛 Troubleshooting

### Common Issues

1. **wkhtmltopdf not found**
   ```
   OSError: wkhtmltopdf reported an error
   ```
   **Solution**: Install wkhtmltopdf system dependency

2. **Ollama connection failed**
   ```
   Connection refused to http://192.168.101.66:11434
   ```
   **Solution**: Check Ollama server status and network connectivity

3. **Chrome driver issues** (when using Selenium)
   ```
   WebDriverException: chrome not reachable
   ```
   **Solution**: Install Google Chrome or update Chrome driver

4. **Model not found**
   ```
   Model 'mistral-small3.2:24b' not found
   ```
   **Solution**: Pull the model using `ollama pull mistral-small3.2:24b`

### Logging
The application provides detailed logging. Check console output for debugging information.

## 🔒 Security Notes

- The application processes web content and sends it to external services
- Ensure your Ollama server is properly secured
- Be cautious when processing untrusted URLs
- Consider running in a sandboxed environment for production use

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

---

**Note**: This application requires an active Ollama server with the mistral-small3.2:24b model. Make sure your server is accessible at the configured URL before running the application.
