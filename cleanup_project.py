#!/usr/bin/env python3
"""
Project Cleanup Script
This script cleans the project of unnecessary files, including old data folders.
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_project():
    """Cleans up project files."""
    
    # List of files to delete
    files_to_delete = [
        # Test and check files
        "check_abstract_completeness.py",
        "check_long_abstracts.py", 
        "data_quality_check.py",
        "test_integrated_system.py",
        "test_integrated.log",
        
        # Log files
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
    
    # List of directories to delete
    dirs_to_delete = [
        "__pycache__",
        "web_app/frontend/node_modules",  # Can be reinstalled
    ]
    
    # Old crawler data folders to delete (keeping the latest)
    old_crawler_dirs = [
        "output/mesh_health_insurance_20250626_161720",
        "output/mesh_health_insurance_20250626_161137", 
        "output/mesh_health_insurance_20250626_161051",
        "output/mesh_health_insurance_20250626_160743",
        "output/mesh_health_insurance_20250626_155301",
        "output/mesh_health_insurance_20250626_130840",
    ]
    
    print("🧹 Starting project cleanup...")
    
    # Delete files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Deleted file: {file_path}")
            except Exception as e:
                print(f"❌ Failed to delete file {file_path}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    # Delete directories
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Deleted directory: {dir_path}")
            except Exception as e:
                print(f"❌ Failed to delete directory {dir_path}: {e}")
        else:
            print(f"⚠️ Directory not found: {dir_path}")
    
    # Delete old crawler data
    for dir_path in old_crawler_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Deleted old crawler data: {dir_path}")
            except Exception as e:
                print(f"❌ Failed to delete old crawler data {dir_path}: {e}")
        else:
            print(f"⚠️ Old crawler data not found: {dir_path}")
    
    # Clean Python cache files
    print("\n🧹 Cleaning Python cache files...")
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_dir)
                    print(f"✅ Deleted cache directory: {cache_dir}")
                except Exception as e:
                    print(f"❌ Failed to delete cache directory {cache_dir}: {e}")
    
    # Clean .pyc files
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        try:
            os.remove(pyc_file)
            print(f"✅ Deleted .pyc file: {pyc_file}")
        except Exception as e:
            print(f"❌ Failed to delete .pyc file {pyc_file}: {e}")
    
    print("\n🎉 Project cleanup complete!")
    
    # Display post-cleanup project size
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk("."):
        # Skip .git directory
        if ".git" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except:
                pass
    
    print(f"\n📊 Post-cleanup stats:")
    print(f"   File count: {file_count}")
    print(f"   Total size: {total_size / (1024*1024):.1f} MB")

if __name__ == "__main__":
    # Confirm cleanup
    print("⚠️ WARNING: This script will delete the following:")
    print("   - Test and check files")
    print("   - Log files") 
    print("   - Python cache files")
    print("   - Old crawler data")
    print("   - Frontend test files")
    print("\nAre you sure you want to continue? (y/N): ", end="")
    
    response = input().strip().lower()
    if response in ['y', 'yes']:
        cleanup_project()
    else:
        print("❌ Cleanup cancelled.") 