#!/usr/bin/env python3
"""
Project Cleanup Script
清理專案中不必要的檔案
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_project():
    """清理專案檔案"""
    
    # 要刪除的檔案列表
    files_to_delete = [
        # 測試與檢查檔案
        "check_abstract_completeness.py",
        "check_long_abstracts.py", 
        "data_quality_check.py",
        "test_integrated_system.py",
        "test_integrated.log",
        
        # 日誌檔案
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
    
    # 要刪除的目錄列表
    dirs_to_delete = [
        "__pycache__",
        "web_app/frontend/node_modules",  # 可以重新安裝
    ]
    
    # 要刪除的舊爬蟲資料夾（保留最新的）
    old_crawler_dirs = [
        "output/mesh_health_insurance_20250626_161720",
        "output/mesh_health_insurance_20250626_161137", 
        "output/mesh_health_insurance_20250626_161051",
        "output/mesh_health_insurance_20250626_160743",
        "output/mesh_health_insurance_20250626_155301",
        "output/mesh_health_insurance_20250626_130840",
    ]
    
    print("🧹 開始清理專案...")
    
    # 刪除檔案
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ 已刪除檔案: {file_path}")
            except Exception as e:
                print(f"❌ 刪除檔案失敗 {file_path}: {e}")
        else:
            print(f"⚠️  檔案不存在: {file_path}")
    
    # 刪除目錄
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ 已刪除目錄: {dir_path}")
            except Exception as e:
                print(f"❌ 刪除目錄失敗 {dir_path}: {e}")
        else:
            print(f"⚠️  目錄不存在: {dir_path}")
    
    # 刪除舊爬蟲資料夾
    for dir_path in old_crawler_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ 已刪除舊爬蟲資料: {dir_path}")
            except Exception as e:
                print(f"❌ 刪除舊爬蟲資料失敗 {dir_path}: {e}")
        else:
            print(f"⚠️  舊爬蟲資料不存在: {dir_path}")
    
    # 清理Python快取檔案
    print("\n🧹 清理Python快取檔案...")
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_dir)
                    print(f"✅ 已刪除快取目錄: {cache_dir}")
                except Exception as e:
                    print(f"❌ 刪除快取目錄失敗 {cache_dir}: {e}")
    
    # 清理.pyc檔案
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        try:
            os.remove(pyc_file)
            print(f"✅ 已刪除.pyc檔案: {pyc_file}")
        except Exception as e:
            print(f"❌ 刪除.pyc檔案失敗 {pyc_file}: {e}")
    
    print("\n🎉 專案清理完成！")
    
    # 顯示清理後的專案大小
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk("."):
        # 跳過.git目錄
        if ".git" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except:
                pass
    
    print(f"\n📊 清理後統計:")
    print(f"   檔案數量: {file_count}")
    print(f"   總大小: {total_size / (1024*1024):.1f} MB")

if __name__ == "__main__":
    # 確認清理
    print("⚠️  警告：此腳本將刪除以下內容：")
    print("   - 測試和檢查檔案")
    print("   - 日誌檔案") 
    print("   - Python快取檔案")
    print("   - 舊的爬蟲資料")
    print("   - 前端測試檔案")
    print("\n請確認您要繼續清理？(y/N): ", end="")
    
    response = input().strip().lower()
    if response in ['y', 'yes']:
        cleanup_project()
    else:
        print("❌ 清理已取消") 