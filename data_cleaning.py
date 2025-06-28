#!/usr/bin/env python3
"""
Data cleaning script
Handle duplicate PMIDs, missing titles and abstracts, and other data quality issues
"""

import json
import pandas as pd
from collections import OrderedDict
from datetime import datetime
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """Data cleaner"""
    
    def __init__(self, input_file):
        """Initialize cleaner"""
        self.input_file = Path(input_file)
        self.data = None
        self.cleaned_data = []
        self.cleaning_report = {
            'original_count': 0,
            'duplicates_removed': 0,
            'no_title_removed': 0,
            'no_abstract_removed': 0,
            'short_abstract_removed': 0,
            'final_count': 0,
            'removed_articles': []
        }
    
    def load_data(self):
        """Load original data"""
        logger.info(f"Loading data file: {self.input_file}")
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.cleaning_report['original_count'] = len(self.data)
            logger.info(f"Successfully loaded {len(self.data):,} articles")
            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False
    
    def remove_duplicates(self):
        """Remove duplicate PMIDs"""
        logger.info("Starting to remove duplicate PMIDs...")
        
        # Use OrderedDict to maintain order, later entries will overwrite earlier ones
        unique_articles = OrderedDict()
        duplicates_found = 0
        
        for article in self.data:
            pmid = article.get('pmid')
            if pmid:
                if pmid in unique_articles:
                    duplicates_found += 1
                    # Record removed duplicate articles
                    self.cleaning_report['removed_articles'].append({
                        'pmid': pmid,
                        'title': article.get('title', ''),
                        'reason': 'duplicate_pmid',
                        'removed_at': 'duplicate_removal'
                    })
                else:
                    unique_articles[pmid] = article
        
        self.data = list(unique_articles.values())
        self.cleaning_report['duplicates_removed'] = duplicates_found
        
        logger.info(f"Removed {duplicates_found} duplicate PMIDs")
        logger.info(f"Remaining {len(self.data):,} articles")
    
    def remove_invalid_articles(self):
        """Remove invalid articles (missing titles, abstracts, etc.)"""
        logger.info("Starting to remove invalid articles...")
        
        valid_articles = []
        no_title_count = 0
        no_abstract_count = 0
        short_abstract_count = 0
        
        for article in self.data:
            # Safely get title and abstract, handle None values
            title = article.get('title')
            if title is None:
                title = ''
            else:
                title = str(title).strip()
            
            abstract = article.get('abstract')
            if abstract is None:
                abstract = ''
            else:
                abstract = str(abstract).strip()
            
            # Check title
            if not title:
                no_title_count += 1
                self.cleaning_report['removed_articles'].append({
                    'pmid': article.get('pmid'),
                    'title': '',
                    'reason': 'no_title',
                    'removed_at': 'validation'
                })
                continue
            
            # Check abstract
            if not abstract:
                no_abstract_count += 1
                self.cleaning_report['removed_articles'].append({
                    'pmid': article.get('pmid'),
                    'title': title,
                    'reason': 'no_abstract',
                    'removed_at': 'validation'
                })
                continue
            
            # Check abstract length (less than 50 characters)
            if len(abstract) < 50:
                short_abstract_count += 1
                self.cleaning_report['removed_articles'].append({
                    'pmid': article.get('pmid'),
                    'title': title,
                    'reason': 'short_abstract',
                    'removed_at': 'validation'
                })
                continue
            
            # Pass all checks, keep article
            valid_articles.append(article)
        
        self.data = valid_articles
        self.cleaning_report['no_title_removed'] = no_title_count
        self.cleaning_report['no_abstract_removed'] = no_abstract_count
        self.cleaning_report['short_abstract_removed'] = short_abstract_count
        
        logger.info(f"Removal statistics:")
        logger.info(f"  - Missing titles: {no_title_count}")
        logger.info(f"  - Missing abstracts: {no_abstract_count}")
        logger.info(f"  - Short abstracts: {short_abstract_count}")
        logger.info(f"Remaining {len(self.data):,} articles")
    
    def standardize_data(self):
        """Standardize data format"""
        logger.info("Starting data format standardization...")
        
        for article in self.data:
            # Safely handle all fields, ensure they are not None
            title = article.get('title')
            article['title'] = str(title).strip() if title is not None else ''
            
            abstract = article.get('abstract')
            article['abstract'] = str(abstract).strip() if abstract is not None else ''
            
            journal = article.get('journal')
            article['journal'] = str(journal).strip() if journal is not None else ''
            
            pub_date = article.get('pub_date')
            article['pub_date'] = str(pub_date).strip() if pub_date is not None else ''
            
            doi = article.get('doi')
            article['doi'] = str(doi).strip() if doi is not None else ''
            
            # Ensure list fields are lists
            if not isinstance(article.get('authors'), list):
                article['authors'] = []
            if not isinstance(article.get('mesh_terms'), list):
                article['mesh_terms'] = []
            if not isinstance(article.get('pub_types'), list):
                article['pub_types'] = []
            
            # Clean author names
            article['authors'] = [str(author).strip() for author in article['authors'] if author and str(author).strip()]
            
            # Clean MeSH terms
            article['mesh_terms'] = [str(term).strip() for term in article['mesh_terms'] if term and str(term).strip()]
            
            # Clean publication types
            article['pub_types'] = [str(ptype).strip() for ptype in article['pub_types'] if ptype and str(ptype).strip()]
        
        logger.info("Data format standardization completed")
    
    def generate_cleaning_report(self, output_dir):
        """Generate cleaning report"""
        logger.info("Generating cleaning report...")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Update final statistics
        self.cleaning_report['final_count'] = len(self.data)
        
        # Generate detailed report
        report_file = output_dir / "data_cleaning_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PubMed Health Insurance Literature Data Cleaning Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Cleaning time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Original data file: {self.input_file}\n\n")
            
            f.write("Cleaning statistics:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Original article count: {self.cleaning_report['original_count']:,}\n")
            f.write(f"Duplicate PMIDs removed: {self.cleaning_report['duplicates_removed']:,}\n")
            f.write(f"Missing titles removed: {self.cleaning_report['no_title_removed']:,}\n")
            f.write(f"Missing abstracts removed: {self.cleaning_report['no_abstract_removed']:,}\n")
            f.write(f"Short abstracts removed: {self.cleaning_report['short_abstract_removed']:,}\n")
            f.write(f"Final article count: {self.cleaning_report['final_count']:,}\n")
            f.write(f"Retention rate: {self.cleaning_report['final_count']/self.cleaning_report['original_count']*100:.1f}%\n\n")
            
            # Detailed list of removed articles
            f.write("Detailed list of removed articles:\n")
            f.write("-" * 30 + "\n")
            for article in self.cleaning_report['removed_articles'][:100]:  # Only show first 100
                f.write(f"PMID: {article['pmid']}, Title: {article['title'][:100]}..., Reason: {article['reason']}\n")
            
            if len(self.cleaning_report['removed_articles']) > 100:
                f.write(f"... and {len(self.cleaning_report['removed_articles']) - 100} more articles were removed\n")
        
        # Generate CSV of removed articles
        removed_df = pd.DataFrame(self.cleaning_report['removed_articles'])
        removed_file = output_dir / "removed_articles.csv"
        removed_df.to_csv(removed_file, index=False, encoding='utf-8')
        
        # Generate cleaning statistics CSV
        stats_data = {
            'metric': ['original_count', 'duplicates_removed', 'no_title_removed', 
                      'no_abstract_removed', 'short_abstract_removed', 'final_count'],
            'count': [self.cleaning_report['original_count'], 
                     self.cleaning_report['duplicates_removed'],
                     self.cleaning_report['no_title_removed'],
                     self.cleaning_report['no_abstract_removed'],
                     self.cleaning_report['short_abstract_removed'],
                     self.cleaning_report['final_count']]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_file = output_dir / "cleaning_statistics.csv"
        stats_df.to_csv(stats_file, index=False, encoding='utf-8')
        
        logger.info(f"Cleaning report generated at: {output_dir}")
        return output_dir
    
    def save_cleaned_data(self, output_dir):
        """Save cleaned data"""
        logger.info("Saving cleaned data...")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Save as JSON format
        json_file = output_dir / "cleaned_articles.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        # Save as CSV format (main fields)
        csv_data = []
        for article in self.data:
            csv_data.append({
                'pmid': article.get('pmid'),
                'title': article.get('title'),
                'abstract': article.get('abstract'),
                'journal': article.get('journal'),
                'pub_date': article.get('pub_date'),
                'doi': article.get('doi'),
                'authors': '; '.join(article.get('authors', [])),
                'mesh_terms': '; '.join(article.get('mesh_terms', [])),
                'pub_types': '; '.join(article.get('pub_types', []))
            })
        
        csv_df = pd.DataFrame(csv_data)
        csv_file = output_dir / "cleaned_articles.csv"
        csv_df.to_csv(csv_file, index=False, encoding='utf-8')
        
        logger.info(f"Cleaned data saved:")
        logger.info(f"  - JSON: {json_file}")
        logger.info(f"  - CSV: {csv_file}")
        
        return json_file, csv_file
    
    def run_cleaning(self, output_dir):
        """Execute complete cleaning workflow"""
        logger.info("Starting data cleaning...")
        
        if not self.load_data():
            return False
        
        # Execute cleaning steps
        self.remove_duplicates()
        self.remove_invalid_articles()
        self.standardize_data()
        
        # Generate report and save data
        report_dir = self.generate_cleaning_report(output_dir)
        json_file, csv_file = self.save_cleaned_data(output_dir)
        
        logger.info("Data cleaning completed!")
        return True

def main():
    """Main function"""
    # Set file paths
    input_file = "output/mesh_health_insurance_20250626_170522/articles_all_years.json"
    output_dir = "output/cleaned_data"
    
    # Create cleaner and execute cleaning
    cleaner = DataCleaner(input_file)
    success = cleaner.run_cleaning(output_dir)
    
    if success:
        print(f"\n✅ Data cleaning completed!")
        print(f"📊 Original articles: {cleaner.cleaning_report['original_count']:,}")
        print(f"🧹 Cleaned articles: {cleaner.cleaning_report['final_count']:,}")
        print(f"📈 Retention rate: {cleaner.cleaning_report['final_count']/cleaner.cleaning_report['original_count']*100:.1f}%")
        print(f"📁 Output location: {output_dir}")
        print(f"📄 Files included:")
        print(f"   - cleaned_articles.json (cleaned JSON)")
        print(f"   - cleaned_articles.csv (cleaned CSV)")
        print(f"   - data_cleaning_report.txt (cleaning report)")
        print(f"   - cleaning_statistics.csv (cleaning statistics)")
        print(f"   - removed_articles.csv (removed articles)")
    else:
        print("❌ Data cleaning failed!")

if __name__ == "__main__":
    main() 