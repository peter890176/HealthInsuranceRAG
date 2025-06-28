#!/usr/bin/env python3
"""
View articles with long abstracts
Analyze abstract content structure to determine if it's a format issue or actual content
"""

import json
import re
from pathlib import Path

def load_data(file_path):
    """Load data"""
    print(f"Loading data file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Total articles: {len(data):,}")
    return data

def analyze_long_abstracts(data, min_length=2000, sample_size=10):
    """Analyze articles with long abstracts"""
    print(f"\n=== Analyzing articles with abstracts longer than {min_length} characters ===")
    
    # Find articles with long abstracts
    long_abstracts = []
    for article in data:
        abstract = article.get('abstract', '')
        if len(abstract) > min_length:
            long_abstracts.append({
                'pmid': article.get('pmid'),
                'title': article.get('title', ''),
                'abstract_length': len(abstract),
                'abstract': abstract[:500] + '...' if len(abstract) > 500 else abstract,
                'journal': article.get('journal', ''),
                'pub_date': article.get('pub_date', ''),
                'authors': article.get('authors', [])
            })
    
    print(f"Found {len(long_abstracts)} articles with abstracts longer than {min_length} characters")
    
    if not long_abstracts:
        print("No articles with long abstracts found")
        return
    
    # Sort by abstract length
    long_abstracts.sort(key=lambda x: x['abstract_length'], reverse=True)
    
    # Display first few as samples
    print(f"\n=== Top {sample_size} articles with longest abstracts ===")
    for i, article in enumerate(long_abstracts[:sample_size], 1):
        print(f"\n--- Article {i} ---")
        print(f"PMID: {article['pmid']}")
        print(f"Title: {article['title']}")
        print(f"Journal: {article['journal']}")
        print(f"Publication Date: {article['pub_date']}")
        print(f"Authors: {', '.join(article['authors'][:3])}{'...' if len(article['authors']) > 3 else ''}")
        print(f"Abstract Length: {article['abstract_length']:,} characters")
        print(f"First 500 characters: {article['abstract']}")
        
        # Analyze abstract structure
        abstract = article['abstract']
        lines = abstract.split('\n')
        print(f"Number of lines: {len(lines)}")
        print(f"First 5 lines:")
        for j, line in enumerate(lines[:5], 1):
            print(f"  Line {j}: {line[:100]}{'...' if len(line) > 100 else ''}")
    
    # Statistical analysis
    lengths = [article['abstract_length'] for article in long_abstracts]
    print(f"\n=== Abstract Length Statistics ===")
    print(f"Average length: {sum(lengths) / len(lengths):,.0f} characters")
    print(f"Shortest length: {min(lengths):,} characters")
    print(f"Longest length: {max(lengths):,} characters")
    
    # Analyze potential format issues
    print(f"\n=== Format Issue Analysis ===")
    format_issues = {
        'contains_methods': 0,
        'contains_results': 0,
        'contains_conclusions': 0,
        'contains_keywords': 0,
        'contains_references': 0,
        'multiple_paragraphs': 0
    }
    
    for article in long_abstracts:
        abstract = article['abstract'].lower()
        if 'methods' in abstract or 'methodology' in abstract:
            format_issues['contains_methods'] += 1
        if 'results' in abstract or 'findings' in abstract:
            format_issues['contains_results'] += 1
        if 'conclusion' in abstract or 'conclusions' in abstract:
            format_issues['contains_conclusions'] += 1
        if 'keywords' in abstract or 'key words' in abstract:
            format_issues['contains_keywords'] += 1
        if 'reference' in abstract or 'bibliography' in abstract:
            format_issues['contains_references'] += 1
        if abstract.count('\n') > 5:
            format_issues['multiple_paragraphs'] += 1
    
    for issue, count in format_issues.items():
        percentage = (count / len(long_abstracts)) * 100
        print(f"{issue}: {count:,} ({percentage:.1f}%)")
    
    return long_abstracts

def save_long_abstracts_sample(long_abstracts, output_file, sample_size=50):
    """Save sample of articles with long abstracts"""
    sample = long_abstracts[:sample_size]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Sample Analysis of Articles with Long Abstracts\n")
        f.write("=" * 50 + "\n\n")
        
        for i, article in enumerate(sample, 1):
            f.write(f"Article {i}\n")
            f.write("-" * 30 + "\n")
            f.write(f"PMID: {article['pmid']}\n")
            f.write(f"Title: {article['title']}\n")
            f.write(f"Journal: {article['journal']}\n")
            f.write(f"Publication Date: {article['pub_date']}\n")
            f.write(f"Authors: {', '.join(article['authors'])}\n")
            f.write(f"Abstract Length: {article['abstract_length']:,} characters\n")
            f.write(f"Complete Abstract:\n{article['abstract']}\n")
            f.write("\n" + "="*50 + "\n\n")
    
    print(f"Long abstract sample saved to: {output_file}")

def main():
    """Main function"""
    # Set file paths
    data_file = "output/mesh_health_insurance_20250626_170522/articles_all_years.json"
    output_file = "output/data_quality_analysis/long_abstracts_sample.txt"
    
    # Load data
    data = load_data(data_file)
    
    # Analyze articles with long abstracts
    long_abstracts = analyze_long_abstracts(data, min_length=2000, sample_size=10)
    
    if long_abstracts:
        # Save sample
        Path(output_file).parent.mkdir(exist_ok=True)
        save_long_abstracts_sample(long_abstracts, output_file, sample_size=50)
        
        print(f"\n✅ Long abstract analysis completed!")
        print(f"📄 Detailed sample saved to: {output_file}")
        print(f"💡 Suggestions:")
        print(f"   - Check if these articles contain complete content like methods, results, conclusions")
        print(f"   - Determine if they are full text rather than abstracts")
        print(f"   - Consider truncating or removing these articles")
    else:
        print("No articles found for analysis")

if __name__ == "__main__":
    main() 