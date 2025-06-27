#!/usr/bin/env python3
"""
Test script for Safespill Hangar Projects Scraper
This script tests basic functionality without requiring API keys
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from config import Config
        config = Config()
        print("✓ Configuration loaded successfully")
        print(f"  - Reports directory: {config.REPORTS_DIR}")
        print(f"  - Schedule time: {config.SCHEDULE_TIME}")
        print(f"  - Schedule day: {config.SCHEDULE_DAY}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False

def test_excel_handler():
    """Test Excel handler functionality"""
    print("\nTesting Excel handler...")
    try:
        from excel_handler import ExcelHandler
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = [
                {
                    'Project Title': 'Test Hangar Project',
                    'Source URL': 'https://example.com/test-article',
                    'Summary': 'This is a test summary for a hangar project',
                    'Country/Region': 'United States',
                    'Language': 'English',
                    'Date Published': '2024-01-15',
                    'Week Collected': '2024-01-15'
                }
            ]
            
            # Test Excel handler
            handler = ExcelHandler('uk_na')
            handler.reports_dir = temp_dir  # Use temporary directory
            
            # Test file creation
            filepath = handler.create_new_excel(test_data)
            print(f"✓ Excel file created: {filepath}")
            
            # Test file info
            file_info = handler.get_file_info()
            print(f"✓ File info retrieved: {file_info['row_count']} rows")
            
            # Test duplicate filtering
            new_articles = handler.filter_new_articles(test_data)
            print(f"✓ Duplicate filtering: {len(new_articles)} new articles")
            
        return True
    except Exception as e:
        print(f"✗ Excel handler test failed: {str(e)}")
        return False

def test_email_sender():
    """Test email sender functionality"""
    print("\nTesting email sender...")
    try:
        from email_sender import EmailSender
        
        sender = EmailSender()
        
        # Test email body creation
        body = sender._create_email_body('uk_na', 5, '2024-01-15')
        if body and 'Safespill' in body:
            print("✓ Email body creation successful")
        else:
            print("✗ Email body creation failed")
            return False
        
        # Test configuration check
        config_test = sender.test_email_configuration()
        if not config_test:
            print("⚠ Email configuration not set (this is expected for testing)")
        else:
            print("✓ Email configuration test passed")
        
        return True
    except Exception as e:
        print(f"✗ Email sender test failed: {str(e)}")
        return False

def test_scheduler():
    """Test scheduler functionality"""
    print("\nTesting scheduler...")
    try:
        from scheduler import ScrapingScheduler
        
        scheduler = ScrapingScheduler()
        
        # Test scheduling
        def test_function():
            print("Test function executed")
        
        scheduler.schedule_weekly_run(test_function)
        print("✓ Scheduler created successfully")
        
        # Test next run time
        next_run = scheduler.get_next_run_time()
        print(f"✓ Next run time: {next_run}")
        
        return True
    except Exception as e:
        print(f"✗ Scheduler test failed: {str(e)}")
        return False

def test_imports():
    """Test all module imports"""
    print("Testing module imports...")
    
    modules = [
        'config',
        'news_scraper', 
        'excel_handler',
        'email_sender',
        'scheduler'
    ]
    
    all_imports_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {str(e)}")
            all_imports_ok = False
    
    return all_imports_ok

def test_directory_structure():
    """Test directory structure creation"""
    print("\nTesting directory structure...")
    try:
        from config import Config
        config = Config()
        
        # Test reports directory
        if not os.path.exists(config.REPORTS_DIR):
            os.makedirs(config.REPORTS_DIR)
            print(f"✓ Created reports directory: {config.REPORTS_DIR}")
        else:
            print(f"✓ Reports directory exists: {config.REPORTS_DIR}")
        
        # Test data directory
        if not os.path.exists(config.DATA_DIR):
            os.makedirs(config.DATA_DIR)
            print(f"✓ Created data directory: {config.DATA_DIR}")
        else:
            print(f"✓ Data directory exists: {config.DATA_DIR}")
        
        return True
    except Exception as e:
        print(f"✗ Directory structure test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Safespill Hangar Projects Scraper - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Directory Structure", test_directory_structure),
        ("Excel Handler", test_excel_handler),
        ("Email Sender", test_email_sender),
        ("Scheduler", test_scheduler)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scraper is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with SERPAPI_KEY")
        print("2. Run: python main.py test")
        print("3. Run: python main.py backfill")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 