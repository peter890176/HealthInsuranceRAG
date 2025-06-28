#!/usr/bin/env python3
"""
Integrated System Test for PubMed Health Insurance Literature Crawler

This script tests the complete functionality including:
- PubMed API connectivity
- MeSH query building
- Data parsing
- APA citation generation
- File output formats
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import PubMedDataParser, APACitationGenerator, FileHandler
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_integrated.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_pubmed_api_connectivity():
    """Test PubMed API connectivity"""
    print("=== Testing PubMed API Connectivity ===")
    
    try:
        import requests
        
        # Test basic search
        url = f"{Config.BASE_URL}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": "health insurance",
            "retmax": 1,
            "retmode": "json"
        }
        
        if Config.API_KEY:
            params["api_key"] = Config.API_KEY
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        count = int(data["esearchresult"]["count"])
        
        print(f"✅ API connectivity test passed")
        print(f"   Found {count:,} articles for 'health insurance'")
        return True
        
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False

def test_mesh_query_building():
    """Test MeSH query building"""
    print("\n=== Testing MeSH Query Building ===")
    
    try:
        mesh_terms = [
            '"Insurance, Health"[MeSH Terms]',
            '"Insurance Coverage"[MeSH Terms]',
            '"Health Policy"[MeSH Terms]'
        ]
        
        # Build query
        mesh_query = " OR ".join(mesh_terms)
        full_query = f"({mesh_query}) AND hasabstract AND \"English\"[Language] AND 2020:2025[Date - Publication]"
        
        print(f"✅ MeSH query building test passed")
        print(f"   Query: {full_query}")
        return full_query
        
    except Exception as e:
        print(f"❌ MeSH query building test failed: {e}")
        return None

def test_data_parsing():
    """Test XML data parsing"""
    print("\n=== Testing Data Parsing ===")
    
    try:
        # Sample XML data (simplified)
        sample_xml = '''<?xml version="1.0" ?>
<PubmedArticleSet>
<PubmedArticle>
<MedlineCitation>
<PMID>12345678</PMID>
<Article>
<Journal>
<Title>Test Journal</Title>
</Journal>
<ArticleTitle>Test Article Title</ArticleTitle>
<Abstract>
<AbstractText>This is a test abstract.</AbstractText>
</Abstract>
<AuthorList>
<Author>
<LastName>Smith</LastName>
<ForeName>John</ForeName>
</Author>
<Author>
<LastName>Doe</LastName>
<ForeName>Jane</ForeName>
</Author>
</AuthorList>
</Article>
<PubDate>
<Year>2023</Year>
<Month>Jun</Month>
<Day>15</Day>
</PubDate>
</MedlineCitation>
</PubmedArticle>
</PubmedArticleSet>'''
        
        # Parse XML
        articles = PubMedDataParser.parse_xml_abstracts(sample_xml)
        
        if articles and len(articles) > 0:
            article = articles[0]
            print(f"✅ Data parsing test passed")
            print(f"   Parsed {len(articles)} article(s)")
            print(f"   PMID: {article.get('pmid')}")
            print(f"   Title: {article.get('title')}")
            print(f"   Authors: {article.get('authors')}")
            return articles
        else:
            print(f"❌ Data parsing test failed: No articles parsed")
            return None
            
    except Exception as e:
        print(f"❌ Data parsing test failed: {e}")
        return None

def test_apa_citation_generation(articles):
    """Test APA citation generation"""
    print("\n=== Testing APA Citation Generation ===")
    
    if not articles:
        print("❌ APA citation test skipped: No articles provided")
        return False
    
    try:
        # Generate APA citations
        references = APACitationGenerator.create_apa_reference_list(articles)
        
        if references and len(references) > 0:
            print(f"✅ APA citation generation test passed")
            print(f"   Generated {len(references)} citation(s)")
            print(f"   Sample citation: {references[0]}")
            return references
        else:
            print(f"❌ APA citation generation test failed: No citations generated")
            return None
            
    except Exception as e:
        print(f"❌ APA citation generation test failed: {e}")
        return None

def test_file_output_formats(articles, references):
    """Test file output formats"""
    print("\n=== Testing File Output Formats ===")
    
    try:
        # Create test output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_output_dir = Path(f"test_output_{timestamp}")
        test_output_dir.mkdir(exist_ok=True)
        
        # Test JSON output
        json_file = test_output_dir / "test_articles.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        # Test TXT output
        txt_file = test_output_dir / "test_articles.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            for i, article in enumerate(articles, 1):
                f.write(f"=== Article {i} ===\n")
                f.write(f"PMID: {article.get('pmid', 'N/A')}\n")
                f.write(f"Title: {article.get('title', 'N/A')}\n")
                
                # Handle abstract with proper formatting
                abstract = article.get('abstract', 'N/A')
                if abstract and abstract != 'N/A':
                    f.write(f"Abstract: {abstract}\n")
                else:
                    f.write(f"Abstract: No abstract available\n")
                
                # Handle authors with better formatting
                authors = article.get('authors', [])
                if authors:
                    f.write(f"Authors: {'; '.join(authors)}\n")
                else:
                    f.write(f"Authors: No authors listed\n")
                
                f.write(f"Journal: {article.get('journal', 'N/A')}\n")
                f.write(f"Publication Date: {article.get('pub_date', 'N/A')}\n")
                f.write(f"Volume: {article.get('volume', 'N/A')}\n")
                f.write(f"Issue: {article.get('issue', 'N/A')}\n")
                f.write(f"Pages: {article.get('pages', 'N/A')}\n")
                f.write(f"DOI: {article.get('doi', 'N/A')}\n")
                
                # Handle MeSH terms with better formatting
                mesh_terms = article.get('mesh_terms', [])
                if mesh_terms:
                    f.write(f"MeSH Terms: {'; '.join(mesh_terms)}\n")
                else:
                    f.write(f"MeSH Terms: No MeSH terms available\n")
                
                # Handle publication types with better formatting
                pub_types = article.get('pub_types', [])
                if pub_types:
                    f.write(f"Publication Types: {'; '.join(pub_types)}\n")
                else:
                    f.write(f"Publication Types: No publication types listed\n")
                
                # Add APA Reference
                apa_citation = APACitationGenerator.create_apa_citation(article)
                f.write(f"APA Reference: {apa_citation}\n")
                
                f.write("\n" + "="*50 + "\n\n")
        
        # Test APA references output
        if references:
            apa_file = test_output_dir / "test_apa_references.txt"
            with open(apa_file, 'w', encoding='utf-8') as f:
                f.write("APA Reference List\n")
                f.write("=" * 50 + "\n\n")
                for i, ref in enumerate(references, 1):
                    f.write(f"{i}. {ref}\n\n")
        
        print(f"✅ File output test passed")
        print(f"   Output directory: {test_output_dir}")
        print(f"   Generated files:")
        print(f"     - {json_file.name}")
        print(f"     - {txt_file.name}")
        if references:
            print(f"     - {apa_file.name}")
        
        return test_output_dir
        
    except Exception as e:
        print(f"❌ File output test failed: {e}")
        return None

def test_small_scale_crawling():
    """Test small scale crawling (5 articles)"""
    print("\n=== Testing Small Scale Crawling ===")
    
    try:
        import requests
        
        # Build query
        query = '("Insurance, Health"[MeSH Terms]) AND hasabstract AND "English"[Language] AND 2020:2025[Date - Publication]'
        
        # Search for articles
        url = f"{Config.BASE_URL}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 5,
            "retmode": "json"
        }
        
        if Config.API_KEY:
            params["api_key"] = Config.API_KEY
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        pmids = data["esearchresult"]["idlist"]
        
        if not pmids:
            print("❌ Small scale crawling test failed: No PMIDs found")
            return None
        
        # Fetch abstracts
        fetch_url = f"{Config.BASE_URL}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "rettype": "xml",
            "retmode": "xml"
        }
        
        if Config.API_KEY:
            fetch_params["api_key"] = Config.API_KEY
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=60)
        fetch_response.raise_for_status()
        
        # Parse abstracts
        articles = PubMedDataParser.parse_xml_abstracts(fetch_response.text)
        
        if articles:
            print(f"✅ Small scale crawling test passed")
            print(f"   Retrieved {len(pmids)} PMIDs")
            print(f"   Successfully parsed {len(articles)} articles")
            return articles
        else:
            print("❌ Small scale crawling test failed: No articles parsed")
            return None
            
    except Exception as e:
        print(f"❌ Small scale crawling test failed: {e}")
        return None

def main():
    """Main test function"""
    print("=== Integrated System Test for PubMed Health Insurance Literature Crawler ===")
    print("=" * 80)
    
    # Test results
    test_results = {}
    
    # Test 1: API connectivity
    test_results['api_connectivity'] = test_pubmed_api_connectivity()
    
    # Test 2: MeSH query building
    test_results['mesh_query'] = test_mesh_query_building()
    
    # Test 3: Data parsing
    test_results['data_parsing'] = test_data_parsing()
    
    # Test 4: APA citation generation
    test_results['apa_citation'] = test_apa_citation_generation(test_results.get('data_parsing'))
    
    # Test 5: File output formats
    test_results['file_output'] = test_file_output_formats(
        test_results.get('data_parsing', []),
        test_results.get('apa_citation', [])
    )
    
    # Test 6: Small scale crawling
    test_results['small_crawling'] = test_small_scale_crawling()
    
    # Summary
    print("\n" + "=" * 80)
    print("=== Test Summary ===")
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The system is ready for use.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the issues above.")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main() 