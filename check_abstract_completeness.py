#!/usr/bin/env python3
"""
檢查文章摘要完整性
分析缺失摘要、過短摘要、格式異常等問題
"""

import json
import re
from pathlib import Path
from collections import Counter

def load_data(file_path):
    """載入數據"""
    print(f"載入數據檔案: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"總文章數: {len(data):,}")
    return data

def analyze_abstract_completeness(data):
    """分析摘要完整性"""
    print("\n=== 摘要完整性分析 ===")
    
    # 統計變數
    missing_abstracts = []
    short_abstracts = []
    long_abstracts = []
    normal_abstracts = []
    format_issues = []
    
    for article in data:
        pmid = article.get('pmid', 'Unknown')
        title = article.get('title', '')
        abstract = article.get('abstract', '')
        journal = article.get('journal', '')
        
        # 檢查缺失摘要
        if not abstract or abstract.strip() == '':
            missing_abstracts.append({
                'pmid': pmid,
                'title': title,
                'journal': journal,
                'issue': 'Missing abstract'
            })
            continue
        
        abstract_length = len(abstract.strip())
        
        # 檢查摘要長度
        if abstract_length < 50:
            short_abstracts.append({
                'pmid': pmid,
                'title': title,
                'journal': journal,
                'abstract': abstract,
                'length': abstract_length,
                'issue': 'Very short abstract'
            })
        elif abstract_length > 2000:
            long_abstracts.append({
                'pmid': pmid,
                'title': title,
                'journal': journal,
                'abstract': abstract[:200] + '...',
                'length': abstract_length,
                'issue': 'Very long abstract'
            })
        else:
            normal_abstracts.append({
                'pmid': pmid,
                'title': title,
                'journal': journal,
                'abstract': abstract,
                'length': abstract_length
            })
        
        # 檢查格式問題
        if check_format_issues(abstract):
            format_issues.append({
                'pmid': pmid,
                'title': title,
                'journal': journal,
                'abstract': abstract[:200] + '...',
                'issue': 'Format issues detected'
            })
    
    # 輸出統計結果
    print(f"缺失摘要: {len(missing_abstracts):,} 篇")
    print(f"過短摘要 (<50字): {len(short_abstracts):,} 篇")
    print(f"過長摘要 (>2000字): {len(long_abstracts):,} 篇")
    print(f"格式異常: {len(format_issues):,} 篇")
    print(f"正常摘要: {len(normal_abstracts):,} 篇")
    
    # 計算完整性比例
    total_articles = len(data)
    complete_abstracts = len(normal_abstracts)
    completeness_rate = (complete_abstracts / total_articles) * 100
    
    print(f"\n摘要完整性比例: {completeness_rate:.1f}%")
    
    return {
        'missing': missing_abstracts,
        'short': short_abstracts,
        'long': long_abstracts,
        'format_issues': format_issues,
        'normal': normal_abstracts,
        'completeness_rate': completeness_rate
    }

def check_format_issues(abstract):
    """檢查摘要格式問題"""
    issues = []
    
    # 檢查是否包含過多的特殊字符
    special_char_ratio = len(re.findall(r'[^\w\s\.\,\;\:\!\?\-\(\)]', abstract)) / len(abstract)
    if special_char_ratio > 0.1:
        issues.append('High special character ratio')
    
    # 檢查是否包含明顯的格式標記
    if re.search(r'<[^>]+>', abstract):
        issues.append('Contains HTML tags')
    
    # 檢查是否包含過多的換行
    if abstract.count('\n') > 10:
        issues.append('Too many line breaks')
    
    # 檢查是否包含明顯的錯誤標記
    error_patterns = ['error', 'missing', 'not available', 'n/a', 'null']
    if any(pattern in abstract.lower() for pattern in error_patterns):
        issues.append('Contains error indicators')
    
    return len(issues) > 0

def analyze_journal_distribution(data):
    """分析期刊分布"""
    print("\n=== 期刊分布分析 ===")
    
    journal_counts = Counter()
    journal_abstract_issues = {}
    
    for article in data:
        journal = article.get('journal', 'Unknown')
        abstract = article.get('abstract', '')
        
        journal_counts[journal] += 1
        
        if journal not in journal_abstract_issues:
            journal_abstract_issues[journal] = {
                'total': 0,
                'missing': 0,
                'short': 0,
                'long': 0
            }
        
        journal_abstract_issues[journal]['total'] += 1
        
        if not abstract or abstract.strip() == '':
            journal_abstract_issues[journal]['missing'] += 1
        elif len(abstract.strip()) < 50:
            journal_abstract_issues[journal]['short'] += 1
        elif len(abstract.strip()) > 2000:
            journal_abstract_issues[journal]['long'] += 1
    
    # 顯示前10個期刊的統計
    print("前10個期刊的摘要問題統計:")
    print(f"{'期刊名稱':<50} {'總文章':<8} {'缺失':<6} {'過短':<6} {'過長':<6}")
    print("-" * 80)
    
    for journal, count in journal_counts.most_common(10):
        issues = journal_abstract_issues[journal]
        print(f"{journal[:49]:<50} {issues['total']:<8} {issues['missing']:<6} {issues['short']:<6} {issues['long']:<6}")

def save_analysis_results(results, output_file):
    """保存分析結果"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("文章摘要完整性分析報告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"摘要完整性比例: {results['completeness_rate']:.1f}%\n\n")
        
        # 缺失摘要
        f.write("缺失摘要的文章:\n")
        f.write("-" * 30 + "\n")
        for article in results['missing'][:20]:  # 只顯示前20篇
            f.write(f"PMID: {article['pmid']}\n")
            f.write(f"標題: {article['title']}\n")
            f.write(f"期刊: {article['journal']}\n")
            f.write(f"問題: {article['issue']}\n")
            f.write("\n")
        
        # 過短摘要
        f.write("過短摘要的文章 (<50字):\n")
        f.write("-" * 30 + "\n")
        for article in results['short'][:20]:  # 只顯示前20篇
            f.write(f"PMID: {article['pmid']}\n")
            f.write(f"標題: {article['title']}\n")
            f.write(f"期刊: {article['journal']}\n")
            f.write(f"摘要: {article['abstract']}\n")
            f.write(f"長度: {article['length']} 字\n")
            f.write("\n")
        
        # 格式問題
        f.write("格式異常的文章:\n")
        f.write("-" * 30 + "\n")
        for article in results['format_issues'][:20]:  # 只顯示前20篇
            f.write(f"PMID: {article['pmid']}\n")
            f.write(f"標題: {article['title']}\n")
            f.write(f"期刊: {article['journal']}\n")
            f.write(f"摘要: {article['abstract']}\n")
            f.write(f"問題: {article['issue']}\n")
            f.write("\n")
    
    print(f"\n詳細分析結果已保存到: {output_file}")

def main():
    """主函數"""
    # 設定檔案路徑
    data_file = "output/cleaned_data/cleaned_articles.json"
    output_file = "output/data_quality_analysis/abstract_completeness_report.txt"
    
    # 檢查檔案是否存在
    if not Path(data_file).exists():
        print(f"錯誤: 找不到檔案 {data_file}")
        return
    
    # 載入數據
    data = load_data(data_file)
    
    # 分析摘要完整性
    results = analyze_abstract_completeness(data)
    
    # 分析期刊分布
    analyze_journal_distribution(data)
    
    # 保存結果
    Path(output_file).parent.mkdir(exist_ok=True)
    save_analysis_results(results, output_file)
    
    print(f"\n✅ 摘要完整性檢查完成！")
    print(f"📄 詳細報告已保存到: {output_file}")
    print(f"💡 建議:")
    if results['missing']:
        print(f"   - 有 {len(results['missing'])} 篇文章缺失摘要，需要重新爬取")
    if results['short']:
        print(f"   - 有 {len(results['short'])} 篇文章摘要過短，可能需要檢查")
    if results['format_issues']:
        print(f"   - 有 {len(results['format_issues'])} 篇文章格式異常，需要清理")

if __name__ == "__main__":
    main() 