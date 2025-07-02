#!/usr/bin/env python3
"""
CPU Data Processor Application

This application processes CPU product pages by:
1. Converting web pages to PDF
2. Sending PDFs directly to Ollama LLM for processing
3. Parsing JSON responses and saving to Excel

Author: CPU Data Processor
Date: June 2025
"""

import os
import logging
import tempfile
import base64
import io
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

import requests
import pdfkit
import pandas as pd
import ollama
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pdf2image import convert_from_path
from PIL import Image


class CPUDataProcessor:
    """
    Main class for processing CPU product pages and extracting structured data.
    """
    
    def __init__(self, ollama_url: str = "http://192.168.100.67:11434", 
                 model_name: str = "qwen2.5vl:latest",
                 excel_file: str = "CPU-DATA.xlsx"):
        """
        Initialize the CPU Data Processor.
        
        Args:
            ollama_url: URL of the Ollama API server
            model_name: Name of the model to use
            excel_file: Path to the Excel file for storing data
        """
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.excel_file = excel_file
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Ollama client
        self.ollama_client = ollama.Client(host=ollama_url)
        
        # Setup wkhtmltopdf options
        self.wkhtmltopdf_options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'load-error-handling': 'ignore',
            'load-media-error-handling': 'ignore'
        }
    
    def convert_url_to_pdf(self, url: str) -> str:
        """
        Convert a web page URL to PDF using wkhtmltopdf.
        
        Args:
            url: The URL to convert
            
        Returns:
            Path to the generated PDF file
            
        Raises:
            Exception: If PDF conversion fails
        """
        try:
            self.logger.info(f"Converting URL to PDF: {url}")
            
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                pdf_path = tmp_file.name
            
            # Try with minimal options first
            minimal_options = {
                'page-size': 'A4',
                'encoding': "UTF-8"
            }
            
            try:
                # First attempt with minimal options
                pdfkit.from_url(url, pdf_path, options=minimal_options)
            except Exception as e:
                self.logger.warning(f"First attempt failed: {e}")
                # Second attempt with even more basic options
                basic_options = {'page-size': 'A4'}
                pdfkit.from_url(url, pdf_path, options=basic_options)
            
            self.logger.info(f"PDF created successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"Failed to convert URL to PDF: {str(e)}")
            raise
    
    def convert_url_to_pdf_selenium(self, url: str) -> str:
        """
        Alternative method to convert URL to PDF using Selenium (for dynamic content).
        
        Args:
            url: The URL to convert
            
        Returns:
            Path to the generated PDF file
        """
        try:
            self.logger.info(f"Converting URL to PDF using Selenium: {url}")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Initialize WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Load the page
                driver.get(url)
                
                # Wait for page to load
                import time
                time.sleep(5)
                
                # Get page source
                html_content = driver.page_source
                
                # Create temporary file for PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_path = tmp_file.name
                
                # Convert HTML to PDF with minimal options
                minimal_options = {
                    'page-size': 'A4',
                    'encoding': "UTF-8"
                }
                
                try:
                    pdfkit.from_string(html_content, pdf_path, options=minimal_options)
                except Exception as e:
                    self.logger.warning(f"PDF conversion with minimal options failed: {e}")
                    # Try with even more basic options
                    basic_options = {'page-size': 'A4'}
                    pdfkit.from_string(html_content, pdf_path, options=basic_options)
                
                self.logger.info(f"PDF created successfully using Selenium: {pdf_path}")
                return pdf_path
                
            finally:
                driver.quit()
                
        except Exception as e:
            self.logger.error(f"Failed to convert URL to PDF using Selenium: {str(e)}")
            raise
    
    def send_pdf_to_ollama(self, pdf_path: str) -> Dict[str, Any]:
        """
        Send PDF to Ollama model for processing by converting it to images first.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Parsed JSON response from the model
            
        Raises:
            Exception: If Ollama processing fails
        """
        try:
            self.logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF pages to images
            try:
                images = convert_from_path(pdf_path, dpi=150)
                self.logger.info(f"Converted PDF to {len(images)} images")
            except Exception as e:
                self.logger.error(f"Failed to convert PDF to images: {e}")
                raise
            
            # Convert images to base64
            image_base64_list = []
            for i, image in enumerate(images[:3]):  # Limit to first 3 pages to avoid too much data
                try:
                    # Convert PIL Image to base64
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    image_base64_list.append(img_base64)
                    self.logger.debug(f"Converted page {i+1} to base64")
                except Exception as e:
                    self.logger.warning(f"Failed to convert page {i+1} to base64: {e}")
            
            if not image_base64_list:
                raise Exception("No images were successfully converted from PDF")
            
            # Prepare the prompt
            prompt = """
            Please analyze this CPU product page and extract the following information in JSON format:

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
                "specifications": "additional key specifications as object",
                "url": "source URL if mentioned"
            }

            Extract only the information that is clearly visible in the images. Use null for missing information.
            Ensure the response is a valid JSON object.
            """
            
            self.logger.info(f"Sending {len(image_base64_list)} images to Ollama")
            
            # Send request to Ollama with all images
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': image_base64_list
                    }
                ]
            )
            
            # Parse the response
            response_text = response['message']['content']
            self.logger.info("Received response from Ollama")
            
            # Try to extract JSON from response
            import json
            try:
                # Find JSON in response (it might be wrapped in markdown code blocks)
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif '{' in response_text and '}' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                
                parsed_data = json.loads(json_text)
                self.logger.info("Successfully parsed JSON response")
                return parsed_data
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {str(e)}")
                self.logger.error(f"Response text: {response_text}")
                # Return a basic structure with the raw response
                return {
                    "cpu_id": "unknown",
                    "brand": "unknown", 
                    "model": "unknown",
                    "raw_response": response_text,
                    "parse_error": str(e)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to process PDF with Ollama: {str(e)}")
            raise
    
    def flatten_specifications(self, cpu_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten the 'specifications' dictionary (and any nested dicts like 'memory', 'gpu') into top-level columns.
        """
        flat_data = cpu_data.copy()
        specs = flat_data.pop('specifications', {})
        if isinstance(specs, dict):
            for k, v in specs.items():
                if isinstance(v, dict):
                    for subk, subv in v.items():
                        flat_data[f"{k}_{subk}"] = subv
                else:
                    flat_data[k] = v
        return flat_data

    def save_to_excel(self, cpu_data: Dict[str, Any]) -> None:
        """
        Save or update CPU data in Excel file, flattening specifications into columns.
        
        Args:
            cpu_data: Dictionary containing CPU information
        """
        try:
            self.logger.info("Saving data to Excel file")
            # Flatten specifications
            cpu_data = self.flatten_specifications(cpu_data)
            
            # Check if Excel file exists
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file)
                self.logger.info(f"Loaded existing Excel file with {len(df)} rows")
            else:
                df = pd.DataFrame()
                self.logger.info("Creating new Excel file")
            
            # Convert cpu_data to DataFrame row
            new_row = pd.DataFrame([cpu_data])
            
            # Check if CPU already exists (based on cpu_id or URL)
            cpu_id = cpu_data.get('cpu_id')
            url = cpu_data.get('url')
            
            updated = False
            
            if not df.empty:
                # Check for existing CPU by cpu_id first
                if cpu_id and 'cpu_id' in df.columns:
                    existing_mask = df['cpu_id'] == cpu_id
                    if existing_mask.any():
                        # Update existing row by cpu_id
                        for col in new_row.columns:
                            df.loc[existing_mask, col] = new_row[col].iloc[0]
                        self.logger.info(f"Updated existing CPU by ID: {cpu_id}")
                        updated = True
                
                # If not found by cpu_id, check by URL
                if not updated and url and 'url' in df.columns:
                    existing_mask = df['url'] == url
                    if existing_mask.any():
                        # Update existing row by URL
                        for col in new_row.columns:
                            df.loc[existing_mask, col] = new_row[col].iloc[0]
                        self.logger.info(f"Updated existing CPU by URL: {url}")
                        updated = True
            
            if not updated:
                # Append new row
                df = pd.concat([df, new_row], ignore_index=True)
                self.logger.info(f"Added new CPU: {cpu_id or 'Unknown'}")
            
            # Save to Excel with proper formatting
            df.to_excel(self.excel_file, index=False, engine='openpyxl')
            self.logger.info(f"Data saved to {self.excel_file}")
            
            # Display summary
            print(f"\n📊 Excel Update Summary:")
            print(f"  File: {self.excel_file}")
            print(f"  Total records: {len(df)}")
            print(f"  Action: {'Updated existing' if updated else 'Added new'} record")
            if cpu_id:
                print(f"  CPU ID: {cpu_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save data to Excel: {str(e)}")
            raise
    
    def process_url(self, url: str, use_selenium: bool = False) -> Dict[str, Any]:
        """
        Process a single CPU product page URL.
        
        Args:
            url: The URL to process
            use_selenium: Whether to use Selenium for PDF conversion
            
        Returns:
            Dictionary containing extracted CPU data
        """
        pdf_path = None
        try:
            self.logger.info(f"Processing URL: {url}")
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")
            
            # Convert URL to PDF - try both methods if one fails
            try:
                if use_selenium:
                    pdf_path = self.convert_url_to_pdf_selenium(url)
                else:
                    pdf_path = self.convert_url_to_pdf(url)
            except Exception as e:
                self.logger.warning(f"Primary PDF conversion method failed: {e}")
                # Try the other method as fallback
                try:
                    if use_selenium:
                        self.logger.info("Falling back to wkhtmltopdf...")
                        pdf_path = self.convert_url_to_pdf(url)
                    else:
                        self.logger.info("Falling back to Selenium...")
                        pdf_path = self.convert_url_to_pdf_selenium(url)
                except Exception as fallback_error:
                    self.logger.error(f"Both PDF conversion methods failed. Original: {e}, Fallback: {fallback_error}")
                    raise Exception(f"PDF conversion failed: {fallback_error}")
            
            # Send PDF to Ollama
            cpu_data = self.send_pdf_to_ollama(pdf_path)
            
            # Add source URL to data
            cpu_data['url'] = url
            
            # Save to Excel
            self.save_to_excel(cpu_data)
            
            self.logger.info("URL processing completed successfully")
            return cpu_data
            
        except Exception as e:
            self.logger.error(f"Failed to process URL: {str(e)}")
            raise
        finally:
            # Clean up temporary PDF file
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.unlink(pdf_path)
                    self.logger.debug(f"Cleaned up temporary PDF: {pdf_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up PDF file: {str(e)}")
    
    def run_interactive(self) -> None:
        """
        Run the processor in interactive mode, accepting URLs from user input.
        """
        print("🚀 CPU Data Processor - Interactive Mode")
        print("=" * 50)
        print(f"Ollama Server: {self.ollama_url}")
        print(f"Model: {self.model_name}")
        print(f"Output File: {self.excel_file}")
        print("=" * 50)
        
        while True:
            try:
                print("\nOptions:")
                print("1. Process a URL")
                print("2. Exit")
                
                choice = input("\nEnter your choice (1-2): ").strip()
                
                if choice == '1':
                    url = input("\nEnter CPU product page URL: ").strip()
                    if not url:
                        print("❌ Please enter a valid URL")
                        continue
                    
                    # Ask about Selenium usage
                    use_selenium = input("Use Selenium for dynamic content? (y/N): ").strip().lower() == 'y'
                    
                    print(f"\n🔄 Processing: {url}")
                    try:
                        cpu_data = self.process_url(url, use_selenium=use_selenium)
                        print("✅ Successfully processed URL!")
                        print(f"\n📊 Extracted CPU Information:")
                        print(f"  CPU ID: {cpu_data.get('cpu_id', 'N/A')}")
                        print(f"  Brand: {cpu_data.get('brand', 'N/A')}")
                        print(f"  Model: {cpu_data.get('model', 'N/A')}")
                        print(f"  Cores: {cpu_data.get('cores', 'N/A')}")
                        print(f"  Threads: {cpu_data.get('threads', 'N/A')}")
                        print(f"  Base Clock: {cpu_data.get('base_clock', 'N/A')}")
                        print(f"  Boost Clock: {cpu_data.get('boost_clock', 'N/A')}")
                        print(f"  TDP: {cpu_data.get('tdp', 'N/A')}")
                        
                        # Show Excel file status
                        if os.path.exists(self.excel_file):
                            df = pd.read_excel(self.excel_file)
                            print(f"\n📁 {self.excel_file} now contains {len(df)} total CPU records")
                        
                    except Exception as e:
                        print(f"❌ Error processing URL: {str(e)}")
                        print("💡 Try using Selenium mode for dynamic content or check the URL")
                
                elif choice == '2':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1 or 2.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")


def main():
    """Main function to run the CPU Data Processor."""
    try:
        # Initialize processor
        processor = CPUDataProcessor()
        
        # Run in interactive mode
        processor.run_interactive()
        
    except Exception as e:
        print(f"❌ Failed to start CPU Data Processor: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
