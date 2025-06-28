#!/usr/bin/env python3
"""
Data quality check and cleaning script
For analyzing quality issues in PubMed health insurance literature data
"""

import json
import pandas as pd
import re
from collections import Counter
from datetime import datetime
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityChecker:
    """Data quality checker"""
    
    def __init__(self, data_file_path):
        """Initialize checker"""
        self.data_file_path = Path(data_file_path)
        self.data = None
        self.quality_report = {}
        
    def load_data(self):
        """Load data"""
        logger.info(f"Loading data file: {self.data_file_path}")
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            logger.info(f"Successfully loaded {len(self.data):,} articles")
            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False
    
    def basic_quality_check(self):
        """Basic quality check"""
        logger.info("Running basic quality check...")
        stats = {
            'missing_title': 0,
            'missing_abstract': 0,
            'short_abstract': 0,  # less than 50 chars
            'very_short_abstract': 0,  # less than 20 chars
            'duplicate_pmid': 0,
            'missing_authors': 0,
            'missing_journal': 0,
            'missing_doi': 0,
            'total': len(self.data)
        }
        pmid_set = set()
        for article in self.data:
            # Check each field
            title = article.get('title', '')
            abstract = article.get('abstract', '')
            pmid = article.get('pmid', '')
            authors = article.get('authors', [])
            journal = article.get('journal', '')
            doi = article.get('doi', '')
            
            if not title:
                stats['missing_title'] += 1
            if not abstract:
                stats['missing_abstract'] += 1
            if len(abstract) < 50:
                stats['short_abstract'] += 1
            if len(abstract) < 20:
                stats['very_short_abstract'] += 1
            if not authors:
                stats['missing_authors'] += 1
            if not journal:
                stats['missing_journal'] += 1
            if not doi:
                stats['missing_doi'] += 1
            if pmid in pmid_set:
                stats['duplicate_pmid'] += 1
            else:
                pmid_set.add(pmid)
        self.quality_report['basic_stats'] = stats
        return stats
    
    def content_analysis(self):
        """Content analysis"""
        logger.info("Running content analysis...")
        
        # Journal analysis
        journals = [article.get('journal', 'Unknown') for article in self.data]
        journal_counts = Counter(journals)
        top_journals = journal_counts.most_common(20)
        
        # Author analysis
        all_authors = []
        for article in self.data:
            if article.get('authors'):
                all_authors.extend(article['authors'])
        author_counts = Counter(all_authors)
        top_authors = author_counts.most_common(20)
        
        # Year analysis
        years = []
        for article in self.data:
            pub_date = article.get('pub_date', '')
            if pub_date:
                year_match = re.search(r'(\d{4})', pub_date)
                if year_match:
                    years.append(int(year_match.group(1)))
        year_counts = Counter(years)
        
        # MeSH term analysis
        all_mesh_terms = []
        for article in self.data:
            if article.get('mesh_terms'):
                all_mesh_terms.extend(article['mesh_terms'])
        mesh_counts = Counter(all_mesh_terms)
        top_mesh_terms = mesh_counts.most_common(30)
        
        content_analysis = {
            'top_journals': top_journals,
            'top_authors': top_authors,
            'year_distribution': dict(year_counts),
            'top_mesh_terms': top_mesh_terms,
            'total_unique_journals': len(journal_counts),
            'total_unique_authors': len(author_counts),
            'total_unique_mesh_terms': len(mesh_counts)
        }
        
        self.quality_report['content_analysis'] = content_analysis
        return content_analysis
    
    def data_cleaning_suggestions(self):
        """Data cleaning suggestions"""
        logger.info("Generating data cleaning suggestions...")
        
        suggestions = []
        
        # Check for missing values
        basic_stats = self.quality_report.get('basic_stats', {})
        if basic_stats.get('missing_title', 0) > 0:
            suggestions.append(f"Found {basic_stats['missing_title']} articles missing title")
        
        if basic_stats.get('missing_abstract', 0) > 0:
            suggestions.append(f"Found {basic_stats['missing_abstract']} articles missing abstract")
        
        if basic_stats.get('short_abstract', 0) > 0:
            suggestions.append(f"Found {basic_stats['short_abstract']} articles with short abstract (<50 chars)")
        
        # Check for duplicates
        pmids = [article.get('pmid') for article in self.data]
        unique_pmids = set(pmids)
        if len(pmids) != len(unique_pmids):
            duplicates = len(pmids) - len(unique_pmids)
            suggestions.append(f"Found {duplicates} duplicate PMIDs")
        
        # Check for outliers
        abstract_lengths = [len(article.get('abstract', '')) for article in self.data if article.get('abstract')]
        if abstract_lengths:
            avg_length = sum(abstract_lengths) / len(abstract_lengths)
            very_long = sum(1 for length in abstract_lengths if length > 2000)
            if very_long > 0:
                suggestions.append(f"Found {very_long} articles with very long abstract (>2000 chars)")
        
        self.quality_report['cleaning_suggestions'] = suggestions
        return suggestions
    
    def generate_report(self, output_dir):
        """Generate quality report"""
        logger.info("Generating quality report...")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Generate detailed report
        report_file = output_dir / "data_quality_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PubMed Health Insurance Literature Data Quality Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data file: {self.data_file_path}\n\n")
            
            # Basic statistics
            basic_stats = self.quality_report.get('basic_stats', {})
            f.write("Basic Statistics:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total articles: {basic_stats.get('total', 0):,}\n")
            f.write(f"Missing title: {basic_stats.get('missing_title', 0):,} ({basic_stats.get('missing_title_percentage', 0)}%)\n")
            f.write(f"Missing abstract: {basic_stats.get('missing_abstract', 0):,} ({basic_stats.get('missing_abstract_percentage', 0)}%)\n")
            f.write(f"Short abstract: {basic_stats.get('short_abstract', 0):,} ({basic_stats.get('short_abstract_percentage', 0)}%)\n")
            f.write(f"Very short abstract: {basic_stats.get('very_short_abstract', 0):,} ({basic_stats.get('very_short_abstract_percentage', 0)}%)\n")
            f.write(f"Duplicate PMIDs: {basic_stats.get('duplicate_pmid', 0):,}\n")
            f.write(f"Missing authors: {basic_stats.get('missing_authors', 0):,} ({basic_stats.get('missing_authors_percentage', 0)}%)\n")
            f.write(f"Missing journal: {basic_stats.get('missing_journal', 0):,} ({basic_stats.get('missing_journal_percentage', 0)}%)\n")
            f.write(f"Missing DOI: {basic_stats.get('missing_doi', 0):,} ({basic_stats.get('missing_doi_percentage', 0)}%)\n\n")
            
            # Content analysis
            content_analysis = self.quality_report.get('content_analysis', {})
            f.write("Content Analysis:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total unique journals: {content_analysis.get('total_unique_journals', 0):,}\n")
            f.write(f"Total unique authors: {content_analysis.get('total_unique_authors', 0):,}\n")
            f.write(f"Total unique MeSH terms: {content_analysis.get('total_unique_mesh_terms', 0):,}\n\n")
            
            # Top journals
            f.write("Top Journals (Top 20):\n")
            for i, (journal, count) in enumerate(content_analysis.get('top_journals', [])[:20], 1):
                f.write(f"{i:2d}. {journal}: {count:,}\n")
            f.write("\n")
            
            # Top authors
            f.write("Top Authors (Top 20):\n")
            for i, (author, count) in enumerate(content_analysis.get('top_authors', [])[:20], 1):
                f.write(f"{i:2d}. {author}: {count:,}\n")
            f.write("\n")
            
            # Year distribution
            f.write("Year Distribution:\n")
            year_dist = content_analysis.get('year_distribution', {})
            for year in sorted(year_dist.keys()):
                f.write(f"{year}: {year_dist[year]:,}\n")
            f.write("\n")
            
            # Top MeSH terms
            f.write("Top MeSH Terms (Top 30):\n")
            for i, (term, count) in enumerate(content_analysis.get('top_mesh_terms', [])[:30], 1):
                f.write(f"{i:2d}. {term}: {count:,}\n")
            f.write("\n")
            
            # Cleaning suggestions
            suggestions = self.quality_report.get('cleaning_suggestions', [])
            f.write("Data Cleaning Suggestions:\n")
            f.write("-" * 20 + "\n")
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    f.write(f"{i}. {suggestion}\n")
            else:
                f.write("Data quality is good, no special cleaning needed.\n")
        
        # Generate CSV format statistics
        stats_df = pd.DataFrame([basic_stats])
        stats_file = output_dir / "quality_statistics.csv"
        stats_df.to_csv(stats_file, index=False, encoding='utf-8')
        
        # Generate journal statistics CSV
        journals_df = pd.DataFrame(content_analysis.get('top_journals', []), columns=['Journal', 'Count'])
        journals_file = output_dir / "journal_statistics.csv"
        journals_df.to_csv(journals_file, index=False, encoding='utf-8')
        
        # Generate author statistics CSV
        authors_df = pd.DataFrame(content_analysis.get('top_authors', []), columns=['Author', 'Count'])
        authors_file = output_dir / "author_statistics.csv"
        authors_df.to_csv(authors_file, index=False, encoding='utf-8')
        
        # Generate year statistics CSV
        years_df = pd.DataFrame(list(content_analysis.get('year_distribution', {}).items()), columns=['Year', 'Count'])
        years_df = years_df.sort_values('Year')
        years_file = output_dir / "year_statistics.csv"
        years_df.to_csv(years_file, index=False, encoding='utf-8')
        
        logger.info(f"Quality report generated at: {output_dir}")
        return output_dir
    
    def run_full_analysis(self, output_dir):
        """Run full analysis"""
        logger.info("Starting full data quality analysis...")
        
        if not self.load_data():
            return False
        
        self.basic_quality_check()
        self.content_analysis()
        self.data_cleaning_suggestions()
        
        output_path = self.generate_report(output_dir)
        
        logger.info("Data quality analysis completed!")
        return output_path

def main():
    """Main function"""
    # Set data file path
    data_file = "output/mesh_health_insurance_20250626_170522/articles_all_years.json"
    output_dir = "output/data_quality_analysis"
    
    # Create checker and run analysis
    checker = DataQualityChecker(data_file)
    result = checker.run_full_analysis(output_dir)
    
    if result:
        print(f"\n✅ Data quality analysis completed!")
        print(f"📊 Report location: {result}")
        print(f"📁 Included files:")
        print(f"   - data_quality_report.txt (Detailed report)")
        print(f"   - quality_statistics.csv (Basic statistics)")
        print(f"   - journal_statistics.csv (Journal statistics)")
        print(f"   - author_statistics.csv (Author statistics)")
        print(f"   - year_statistics.csv (Year statistics)")
    else:
        print("❌ Data quality analysis failed!")

if __name__ == "__main__":
    main() 