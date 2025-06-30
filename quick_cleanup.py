#!/usr/bin/env python3
"""
Quick Project Cleanup Script
快速清理專案中最不必要的檔案
"""

import os
import shutil

def quick_cleanup():
    """快速清理專案"""
    
    print("🧹 快速清理專案...")
    
    # 要刪除的檔案
    files_to_delete = [
        # 開發階段使用的檢查檔案
        "check_abstract_completeness.py",
        "check_long_abstracts.py", 
        "data_quality_check.py",
        "test_integrated_system.py",
        "test_integrated.log",
        "mesh_crawler.log",
        
        # 前端測試檔案
        "web_app/frontend/src/App.test.js",
        "web_app/frontend/src/setupTests.js",
        "web_app/frontend/src/reportWebVitals.js",
        "web_app/frontend/src/logo.svg",
        "web_app/frontend/public/logo192.png",
        "web_app/frontend/public/logo512.png",
        "web_app/frontend/README.md",
    ]
    
    # 要刪除的目錄
    dirs_to_delete = [
        "__pycache__",
    ]
    
    # 刪除檔案
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ 已刪除: {file_path}")
            except Exception as e:
                print(f"❌ 刪除失敗 {file_path}: {e}")
    
    # 刪除目錄
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ 已刪除目錄: {dir_path}")
            except Exception as e:
                print(f"❌ 刪除目錄失敗 {dir_path}: {e}")
    
    print("\n🎉 快速清理完成！")

if __name__ == "__main__":
    quick_cleanup() 