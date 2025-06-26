#!/usr/bin/env python3
"""
Test script for CPU Data Processor setup verification
"""

import sys
import subprocess
import importlib
import requests
import tempfile
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing Python package imports...")
    
    packages = [
        'requests', 'bs4', 'selenium', 'pdfkit', 
        'pandas', 'openpyxl', 'ollama'
    ]
    
    failed_imports = []
    for package in packages:
        try:
            if package == 'bs4':
                importlib.import_module('bs4')
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_wkhtmltopdf():
    """Test if wkhtmltopdf is available."""
    print("\n🔍 Testing wkhtmltopdf...")
    
    try:
        result = subprocess.run(['wkhtmltopdf', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  ✅ wkhtmltopdf: {result.stdout.strip()}")
            return True
        else:
            print(f"  ❌ wkhtmltopdf error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ wkhtmltopdf not found: {e}")
        return False

def test_pdf_conversion():
    """Test basic PDF conversion functionality."""
    print("\n🔍 Testing PDF conversion...")
    
    try:
        import pdfkit
        
        # Test with a simple HTML string
        html_content = """
        <html>
        <body>
            <h1>Test Page</h1>
            <p>This is a test for PDF conversion.</p>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8"
        }
        
        try:
            pdfkit.from_string(html_content, pdf_path, options=options)
        except Exception as e:
            # Try with even more basic options if the first attempt fails
            basic_options = {'page-size': 'A4'}
            pdfkit.from_string(html_content, pdf_path, options=basic_options)
        
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print("  ✅ PDF conversion successful")
            os.unlink(pdf_path)  # Clean up
            return True
        else:
            print("  ❌ PDF file not created or empty")
            return False
            
    except Exception as e:
        print(f"  ❌ PDF conversion failed: {e}")
        return False

def test_ollama_connection():
    """Test connection to Ollama server."""
    print("\n🔍 Testing Ollama server connection...")
    
    ollama_url = "http://192.168.101.66:11434"
    
    try:
        # Test basic connectivity
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Ollama server accessible at {ollama_url}")
            
            # Check for models
            data = response.json()
            if 'models' in data and data['models']:
                print(f"  📋 Available models:")
                for model in data['models']:
                    print(f"    - {model.get('name', 'Unknown')}")
                
                # Check for our specific model
                model_names = [m.get('name', '') for m in data['models']]
                if any('qwen2.5vl:latest' in name for name in model_names):
                    print("  ✅ Target model (qwen2.5vl:latest) is available")
                    return True
                else:
                    print("  ⚠️  Target model (qwen2.5vl:latest) not found")
                    print("  💡 You may need to pull it: ollama pull qwen2.5vl:latest")
                    return False
            else:
                print("  ⚠️  No models found on server")
                return False
        else:
            print(f"  ❌ Server responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to Ollama server at {ollama_url}")
        print("  💡 Make sure Ollama is running and accessible")
        return False
    except Exception as e:
        print(f"  ❌ Error testing Ollama: {e}")
        return False

def test_selenium_setup():
    """Test Selenium Chrome setup."""
    print("\n🔍 Testing Selenium Chrome setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Test basic functionality
            driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
            title = driver.title
            driver.quit()
            
            print("  ✅ Selenium Chrome setup working")
            return True
            
        except Exception as e:
            print(f"  ❌ Selenium Chrome setup failed: {e}")
            print("  💡 Try installing Google Chrome: sudo apt install google-chrome-stable")
            return False
            
    except Exception as e:
        print(f"  ❌ Selenium import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 CPU Data Processor - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("wkhtmltopdf", test_wkhtmltopdf),
        ("PDF Conversion", test_pdf_conversion),
        ("Ollama Connection", test_ollama_connection),
        ("Selenium Setup", test_selenium_setup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("You can now run: python cpu_processor.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the main application.")
        print("Check the README.md for setup instructions.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
