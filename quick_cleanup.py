#!/usr/bin/env python3
"""
Quick Project Cleanup Script
Quickly cleans the project of unnecessary files.
"""

import os
import shutil

def quick_cleanup():
    """Quickly clean the project"""
    
    print("🧹 Starting quick project cleanup...")
    
    # Files to delete
    files_to_delete = [
        # Development-stage check files
        "check_abstract_completeness.py",
        "check_long_abstracts.py", 
        "data_quality_check.py",
        "test_integrated_system.py",
        "test_integrated.log",
        "mesh_crawler.log",
        
        # Frontend test files
        "web_app/frontend/src/App.test.js",
        "web_app/frontend/src/setupTests.js",
        "web_app/frontend/src/reportWebVitals.js",
        "web_app/frontend/src/logo.svg",
        "web_app/frontend/public/logo192.png",
        "web_app/frontend/public/logo512.png",
        "web_app/frontend/README.md",
    ]
    
    # Directories to delete
    dirs_to_delete = [
        "__pycache__",
    ]
    
    # Delete files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Deleted: {file_path}")
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
    
    # Delete directories
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Deleted directory: {dir_path}")
            except Exception as e:
                print(f"❌ Failed to delete directory {dir_path}: {e}")
    
    print("\n🎉 Quick cleanup complete!")

if __name__ == "__main__":
    quick_cleanup() 