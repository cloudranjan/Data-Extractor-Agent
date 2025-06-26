#!/usr/bin/env python3
"""
Simple usage example for CPU Data Processor
"""

from cpu_processor import CPUDataProcessor

def main():
    """Simple example of using the CPU processor."""
    
    # Initialize the processor
    processor = CPUDataProcessor(
        ollama_url="http://192.168.101.66:11434",
        model_name="qwen2.5vl:latest",
        excel_file="cpu_data.xlsx"
    )
    
    # Example URLs to process
    urls = [
        "https://www.intel.com/content/www/us/en/products/sku/230496/intel-core-i9-14900k-processor-36m-cache-up-to-6-00-ghz/specifications.html",
        # Add more URLs as needed
    ]
    
    for url in urls:
        try:
            print(f"Processing: {url}")
            cpu_data = processor.process_url(url, use_selenium=True)
            print(f"✅ Success: {cpu_data.get('cpu_id', 'Unknown CPU')}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main()
