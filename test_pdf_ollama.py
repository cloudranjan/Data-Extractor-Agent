#!/usr/bin/env python3
"""
Test script for CPU Data Processor with multiple CPU pages
Tests the update functionality with CPU-DATA.xlsx
"""

from cpu_processor import CPUDataProcessor
import logging
import pandas as pd
import os

def test_interactive_cpu_processing():
    """Interactive test where user provides CPU URLs."""
    
    # Enable info logging
    logging.basicConfig(level=logging.INFO)
    
    processor = CPUDataProcessor()
    
    print(f"🧪 Interactive CPU Data Processor Testing")
    print(f"📁 Output file: CPU-DATA.xlsx")
    print("=" * 60)
    print("💡 Enter CPU product page URLs to process them and update the Excel file.")
    print("💡 Examples:")
    print("   - Intel: https://www.intel.com/content/www/us/en/products/sku/...")
    print("   - AMD: https://www.amd.com/en/products/cpu/...")
    print("   - Any CPU retailer or spec page")
    print("=" * 60)
    
    successful_processes = 0
    url_count = 1
    
    while True:
        try:
            print(f"\n🔗 CPU #{url_count}")
            url = input("Enter CPU product page URL (or 'done' to finish): ").strip()
            
            if not url or url.lower() in ['done', 'exit', 'quit']:
                break
            
            if not url.startswith(('http://', 'https://')):
                print("   ❌ Please enter a valid URL starting with http:// or https://")
                continue
            
            # Ask for processing method
            use_selenium = input("Use Selenium for dynamic content? (y/N): ").strip().lower() == 'y'
            
            print(f"   🔄 Processing: {url}")
            
            try:
                cpu_data = processor.process_url(url, use_selenium=use_selenium)
                
                print(f"   ✅ Success! Extracted data:")
                print(f"      CPU ID: {cpu_data.get('cpu_id', 'N/A')}")
                print(f"      Brand: {cpu_data.get('brand', 'N/A')}")
                print(f"      Model: {cpu_data.get('model', 'N/A')}")
                print(f"      Cores: {cpu_data.get('cores', 'N/A')}")
                print(f"      Threads: {cpu_data.get('threads', 'N/A')}")
                print(f"      TDP: {cpu_data.get('tdp', 'N/A')}")
                
                successful_processes += 1
                url_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
            
            # Show current Excel file status
            if os.path.exists('CPU-DATA.xlsx'):
                df = pd.read_excel('CPU-DATA.xlsx')
                print(f"   📊 CPU-DATA.xlsx now has {len(df)} total records")
                
                # Ask if user wants to see the current data
                show_data = input("   📋 Show current Excel contents? (y/N): ").strip().lower() == 'y'
                if show_data:
                    display_cols = ['cpu_id', 'brand', 'model', 'cores', 'threads', 'base_clock', 'boost_clock', 'tdp']
                    available_cols = [col for col in display_cols if col in df.columns]
                    
                    if available_cols:
                        print("\n   📊 Current CPU Data:")
                        print("   " + df[available_cols].to_string(index=False).replace('\n', '\n   '))
                    else:
                        print("   📊 Current data structure:")
                        print("   " + df.head().to_string(index=False).replace('\n', '\n   '))
        
        except KeyboardInterrupt:
            print("\n\n👋 Processing cancelled by user.")
            break
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📈 Processing Summary:")
    print(f"   URLs processed: {url_count - 1}")
    print(f"   Successful: {successful_processes}")
    print(f"   Failed: {(url_count - 1) - successful_processes}")
    
    # Display final Excel file contents
    if os.path.exists('CPU-DATA.xlsx'):
        df = pd.read_excel('CPU-DATA.xlsx')
        print(f"\n📋 Final CPU-DATA.xlsx Contents ({len(df)} records):")
        
        # Display key columns only for readability
        display_cols = ['cpu_id', 'brand', 'model', 'cores', 'threads', 'base_clock', 'boost_clock', 'tdp']
        available_cols = [col for col in display_cols if col in df.columns]
        
        if available_cols:
            print(df[available_cols].to_string(index=False))
        else:
            print(df.head().to_string(index=False))
    
    return successful_processes > 0

def test_update_functionality():
    """Test that running the same URL updates instead of duplicating."""
    
    print(f"\n🔄 Testing Update Functionality...")
    print("You can test this by entering the same URL multiple times to verify update behavior.")
    
    processor = CPUDataProcessor()
    
    # Ask user for a URL to test update functionality
    print("\nEnter a CPU URL to test update functionality:")
    url = input("URL: ").strip()
    
    if not url or not url.startswith(('http://', 'https://')):
        print("❌ Invalid URL. Skipping update test.")
        return
    
    # Process the URL twice
    for attempt in [1, 2]:
        print(f"\nAttempt {attempt}: Processing {url}")
        try:
            cpu_data = processor.process_url(url, use_selenium=False)
            
            if os.path.exists('CPU-DATA.xlsx'):
                df = pd.read_excel('CPU-DATA.xlsx')
                print(f"   Records in Excel: {len(df)}")
                
                # Check for duplicates
                if 'url' in df.columns:
                    url_count = df['url'].value_counts().get(url, 0)
                    print(f"   Times this URL appears: {url_count}")
                    if attempt == 2 and url_count == 1:
                        print("   ✅ Update functionality working - no duplicates created!")
                    
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    print("🚀 CPU Data Processor - Interactive Testing")
    print("Testing Excel update functionality with CPU-DATA.xlsx")
    print("=" * 60)
    
    print("\nChoose test mode:")
    print("1. Interactive CPU processing (recommended)")
    print("2. Test update functionality")
    print("3. Both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        # Interactive CPU processing
        success = test_interactive_cpu_processing()
    elif choice == '2':
        # Update functionality test
        test_update_functionality()
        success = True
    else:
        # Both tests
        success = test_interactive_cpu_processing()
        if input("\nRun update functionality test? (y/N): ").strip().lower() == 'y':
            test_update_functionality()
    
    if success:
        print("\n🎉 Testing completed! Check CPU-DATA.xlsx for results.")
    else:
        print("\n💥 Some tests failed - check error messages above")
