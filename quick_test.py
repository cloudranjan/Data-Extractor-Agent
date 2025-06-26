#!/usr/bin/env python3
"""
Quick test for the updated CPU processor with better error handling
"""

from cpu_processor import CPUDataProcessor
import logging

def test_simple_conversion():
    """Test with a simple webpage that should work reliably."""
    
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    processor = CPUDataProcessor()
    
    # Test with a simple, reliable URL
    test_url = "https://httpbin.org/html"
    
    print(f"🧪 Testing PDF conversion with: {test_url}")
    
    try:
        # Test both methods
        print("\n1️⃣ Testing with wkhtmltopdf...")
        cpu_data = processor.process_url(test_url, use_selenium=False)
        print("✅ wkhtmltopdf method succeeded!")
        
    except Exception as e:
        print(f"❌ wkhtmltopdf method failed: {e}")
        
        try:
            print("\n2️⃣ Testing with Selenium...")
            cpu_data = processor.process_url(test_url, use_selenium=True)
            print("✅ Selenium method succeeded!")
        except Exception as e2:
            print(f"❌ Selenium method also failed: {e2}")
            return False
    
    return True

if __name__ == "__main__":
    success = test_simple_conversion()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed - please check the error messages above")
