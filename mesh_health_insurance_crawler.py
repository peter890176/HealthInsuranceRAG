#!/usr/bin/env python3
"""
Crawl health insurance related literature abstracts from the past 5 years using MeSH queries

This script uses PubMed API's ESearch and EFetch interfaces,
combines MeSH vocabulary to precisely query health insurance related literature,
and processes all available data in batches by year to avoid 10,000 record limit
"""

import sys
import os
import time
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import PubMedDataParser, FileHandler, APACitationGenerator
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mesh_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MeSHHealthInsuranceCrawler:
    """Crawler class for health insurance literature using MeSH queries with year-based splitting"""
    
    def __init__(self):
        """Initialize crawler"""
        self.api_key = Config.API_KEY
        
        # Create base output folder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_output_dir = Path(f"output/mesh_health_insurance_{timestamp}")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # MeSH query terms
        self.mesh_terms = [
            '"Insurance, Health"[MeSH Terms]',
            '"Insurance Coverage"[MeSH Terms]',
            '"Health Policy"[MeSH Terms]'
        ]
        
        # Query parameters - modified to fetch ALL articles, optimized batch size
        self.target_count = None  # Changed to None to fetch all articles
        self.batch_size = Config.DEFAULT_BATCH_SIZE  # Use batch size from config
        self.search_batch_size = 500  # Reduced search batch size to avoid API limits
        
        # Year range for splitting queries
        self.start_year = 2020
        self.end_year = 2025
        
        logger.info("MeSH Health Insurance Literature Crawler initialized")
        logger.info(f"Target article count: ALL available articles")
        logger.info(f"Base output directory: {self.base_output_dir}")
        logger.info(f"Year range: {self.start_year}-{self.end_year}")
    
    def get_year_queries(self) -> List[Dict]:
        """
        Generate year-based queries to avoid 10,000 record limit
        
        Returns:
            List of dictionaries containing year and query information
        """
        year_queries = []
        
        for year in range(self.start_year, self.end_year + 1):
            year_query = {
                'year': year,
                'date_range': f"{year}[Date - Publication]",
                'query': self.build_mesh_query_for_year(year)
            }
            year_queries.append(year_query)
            
        logger.info(f"Generated {len(year_queries)} year-based queries")
        return year_queries
    
    def build_mesh_query_for_year(self, year: int) -> str:
        """
        Build MeSH query string for specific year
        
        Args:
            year: Target year
            
        Returns:
            Complete query string for the year
        """
        # Combine MeSH terms
        mesh_query = " OR ".join(self.mesh_terms)
        
        # Complete query string with year-specific date range
        full_query = f"({mesh_query}) AND hasabstract AND \"English\"[Language] AND {year}[Date - Publication]"
        
        logger.info(f"Built MeSH query for {year}: {full_query}")
        return full_query
    
    def build_mesh_query(self) -> str:
        """
        Build MeSH query string (kept for backward compatibility)
        
        Returns:
            Complete query string
        """
        # Combine MeSH terms
        mesh_query = " OR ".join(self.mesh_terms)
        
        # Complete query string
        full_query = f"({mesh_query}) AND hasabstract AND \"English\"[Language] AND {self.start_year}:{self.end_year}[Date - Publication]"
        
        logger.info(f"Built MeSH query: {full_query}")
        return full_query
    
    def get_total_count(self, query: str) -> int:
        """
        Get total number of articles matching the query
        
        Args:
            query: Query string
            
        Returns:
            Total article count
        """
        try:
            url = f"{Config.BASE_URL}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": 0,  # Only get count, not IDs
                "retmode": "json"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            total_count = int(data["esearchresult"]["count"])
            
            logger.info(f"Total articles matching query: {total_count}")
            return total_count
            
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            return 0
    
    def search_articles_batch(self, query: str, start: int, count: int, max_retries: int = 3) -> List[str]:
        """
        Batch search article IDs with retry mechanism and fallback strategy
        
        Args:
            query: Query string
            start: Starting position
            count: Number to retrieve
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of PubMed IDs
        """
        for attempt in range(max_retries):
            try:
                url = f"{Config.BASE_URL}/esearch.fcgi"
                params = {
                    "db": "pubmed",
                    "term": query,
                    "retstart": start,
                    "retmax": count,
                    "retmode": "json",
                    "sort": "date"  # Sort by date, prioritize latest articles
                }
                
                if self.api_key:
                    params["api_key"] = self.api_key
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                # Clean response text to handle invalid characters
                response_text = response.text
                # Remove or replace invalid control characters
                response_text = ''.join(char for char in response_text if ord(char) >= 32 or char in '\n\r\t')
                
                data = json.loads(response_text)
                id_list = data["esearchresult"]["idlist"]
                
                logger.info(f"Batch search: position {start}-{start+len(id_list)-1}, retrieved {len(id_list)} IDs")
                return id_list
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}/{max_retries}: {e}")
                
                # Try with smaller batch size on last attempt
                if attempt == max_retries - 1 and count > 100:
                    logger.info(f"Trying with smaller batch size: {count//2}")
                    return self.search_articles_batch(query, start, count//2, 2)
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed to decode JSON after {max_retries} attempts")
                    return []
                    
            except Exception as e:
                logger.warning(f"Batch search failed on attempt {attempt + 1}/{max_retries}: {e}")
                
                # Try with smaller batch size on last attempt
                if attempt == max_retries - 1 and count > 100:
                    logger.info(f"Trying with smaller batch size: {count//2}")
                    return self.search_articles_batch(query, start, count//2, 2)
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Batch search failed after {max_retries} attempts")
                    return []
        
        return []
    
    def fetch_abstracts_batch(self, id_list: List[str], batch_size: int) -> str:
        """
        Batch fetch XML format abstracts
        
        Args:
            id_list: List of PubMed IDs
            batch_size: Batch size
            
        Returns:
            XML format abstract text
        """
        try:
            url = f"{Config.BASE_URL}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "rettype": "xml",
                "retmode": "xml"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Batch fetch abstracts failed: {e}")
            return ""
    
    def crawl_health_insurance_articles(self) -> Dict:
        """
        Main crawling method - now processes by year to avoid 10,000 record limit
        
        Returns:
            Dictionary containing all results from all years
        """
        start_time = time.time()
        logger.info("Starting to crawl health insurance related literature by year")
        
        # Get year-based queries
        year_queries = self.get_year_queries()
        
        # Overall results tracking
        all_years_results = {
            "query": f"Health Insurance Literature {self.start_year}-{self.end_year}",
            "total_found": 0,
            "target_count": "ALL",
            "actual_processed": 0,
            "successful_articles": 0,
            "successful_batches": 0,
            "failed_batches": 0,
            "pmids": [],
            "articles": [],
            "year_results": {},
            "crawl_time": datetime.now().isoformat(),
            "execution_time_seconds": 0
        }
        
        # Process each year
        for year_query in year_queries:
            year = year_query['year']
            query = year_query['query']
            
            logger.info(f"\n=== Processing Year {year} ===")
            
            # Create year-specific output directory
            year_output_dir = self.base_output_dir / f"year_{year}"
            year_output_dir.mkdir(exist_ok=True)
            
            # Process this year
            year_result = self.crawl_single_year(year, query, year_output_dir)
            
            # Add to overall results
            all_years_results["year_results"][year] = year_result
            all_years_results["total_found"] += year_result.get("total_found", 0)
            all_years_results["actual_processed"] += year_result.get("actual_processed", 0)
            all_years_results["successful_articles"] += year_result.get("successful_articles", 0)
            all_years_results["successful_batches"] += year_result.get("successful_batches", 0)
            all_years_results["failed_batches"] += year_result.get("failed_batches", 0)
            all_years_results["pmids"].extend(year_result.get("pmids", []))
            all_years_results["articles"].extend(year_result.get("articles", []))
            
            logger.info(f"Year {year} completed: {year_result.get('successful_articles', 0)} articles")
        
        # Calculate total execution time
        total_time = time.time() - start_time
        all_years_results["execution_time_seconds"] = total_time
        
        logger.info(f"\n=== All Years Completed ===")
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        logger.info(f"Total articles found: {all_years_results['total_found']:,}")
        logger.info(f"Total articles processed: {all_years_results['actual_processed']:,}")
        logger.info(f"Total successful articles: {all_years_results['successful_articles']:,}")
        
        return all_years_results
    
    def crawl_single_year(self, year: int, query: str, output_dir: Path) -> Dict:
        """
        Crawl articles for a single year
        
        Args:
            year: Target year
            query: Query string for the year
            output_dir: Output directory for this year
            
        Returns:
            Dictionary containing results for this year
        """
        logger.info(f"Starting crawl for year {year}")
        
        # Get total count for this year
        total_count = self.get_total_count(query)
        if total_count == 0:
            logger.info(f"No articles found for year {year}")
            return {
                "year": year,
                "query": query,
                "total_found": 0,
                "target_count": "ALL",
                "actual_processed": 0,
                "successful_articles": 0,
                "successful_batches": 0,
                "failed_batches": 0,
                "pmids": [],
                "articles": [],
                "crawl_time": datetime.now().isoformat(),
                "execution_time_seconds": 0
            }
        
        # Calculate number of batches to process
        actual_count = total_count
        search_batches = (actual_count + self.search_batch_size - 1) // self.search_batch_size
        
        logger.info(f"Year {year}: Target article count: {actual_count} (ALL available articles)")
        logger.info(f"Year {year}: Search batch count: {search_batches}")
        
        # Calculate actual abstract batches
        total_fetch_batches = (actual_count + self.batch_size - 1) // self.batch_size
        total_requests = search_batches + total_fetch_batches
        
        logger.info(f"Year {year}: Abstract batch size: {self.batch_size} articles")
        logger.info(f"Year {year}: Estimated abstract batch count: {total_fetch_batches}")
        logger.info(f"Year {year}: Estimated total requests: {search_batches} searches + {total_fetch_batches} abstracts = {total_requests} requests")
        
        # Estimate execution time
        if Config.API_KEY:
            estimated_time = total_requests / 10  # 10 requests per second
            logger.info(f"Year {year}: Estimated execution time: {estimated_time:.1f} seconds (with API Key)")
        else:
            estimated_time = total_requests / 3   # 3 requests per second
            logger.info(f"Year {year}: Estimated execution time: {estimated_time:.1f} seconds (without API Key)")
        
        all_articles = []
        all_pmids = []
        
        # Batch search and fetch
        successful_batches = 0
        failed_batches = 0
        
        for batch_num in range(search_batches):
            batch_start_time = time.time()
            start_pos = batch_num * self.search_batch_size
            batch_count = min(self.search_batch_size, actual_count - start_pos)
            
            logger.info(f"Year {year}: Processing search batch {batch_num + 1}/{search_batches} (position {start_pos}-{start_pos+batch_count-1})")
            
            # Search article IDs
            id_list = self.search_articles_batch(query, start_pos, batch_count)
            if not id_list:
                failed_batches += 1
                logger.warning(f"Year {year}: Batch {batch_num + 1} failed, skipping to next batch")
                continue
            
            successful_batches += 1
            all_pmids.extend(id_list)
            
            # Batch fetch abstracts
            fetch_batches = (len(id_list) + self.batch_size - 1) // self.batch_size
            
            for fetch_batch in range(fetch_batches):
                start_idx = fetch_batch * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(id_list))
                batch_ids = id_list[start_idx:end_idx]
                
                logger.info(f"Year {year}:    Fetching abstract batch {fetch_batch + 1}/{fetch_batches}: {len(batch_ids)} articles")
                
                # Fetch abstracts
                abstracts = self.fetch_abstracts_batch(batch_ids, self.batch_size)
                if abstracts:
                    # Parse abstracts - using optimized parsing function
                    articles = PubMedDataParser.parse_xml_abstracts(abstracts)
                    if articles:
                        all_articles.extend(articles)
                        logger.info(f"Year {year}:      Successfully parsed {len(articles)} articles")
                    else:
                        logger.warning(f"Year {year}:      Parsing failed, no article data obtained")
                else:
                    logger.warning(f"Year {year}:      No abstract data obtained")
            
            batch_time = time.time() - batch_start_time
            logger.info(f"Year {year}: Batch {batch_num + 1} completed, time: {batch_time:.2f} seconds")
            
            # Progress update
            progress = (batch_num + 1) / search_batches * 100
            logger.info(f"Year {year}: Progress: {progress:.1f}% ({batch_num + 1}/{search_batches} batches)")
        
        # Organize results for this year
        year_result = {
            "year": year,
            "query": query,
            "total_found": total_count,
            "target_count": "ALL",
            "actual_processed": len(all_pmids),
            "successful_articles": len(all_articles),
            "successful_batches": successful_batches,
            "failed_batches": failed_batches,
            "pmids": all_pmids,
            "articles": all_articles,
            "crawl_time": datetime.now().isoformat(),
            "execution_time_seconds": time.time() - batch_start_time if 'batch_start_time' in locals() else 0
        }
        
        # Save year-specific results
        self.save_year_results(year_result, output_dir)
        
        logger.info(f"Year {year}: Crawling completed: Processed {len(all_pmids)} PMIDs, successfully parsed {len(all_articles)} articles")
        
        return year_result
    
    def save_year_results(self, year_result: Dict, output_dir: Path):
        """
        Save results for a specific year to its own directory
        
        Args:
            year_result: Results for the specific year
            output_dir: Output directory for this year
        """
        year = year_result['year']
        logger.info(f"Saving year {year} results to {output_dir}")
        
        # Save complete results (JSON)
        json_file = output_dir / f"health_insurance_articles_{year}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(year_result, f, ensure_ascii=False, indent=2)
        
        # Save article list (JSON)
        articles_file = output_dir / f"articles_{year}.json"
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(year_result["articles"], f, ensure_ascii=False, indent=2)
        
        # Save article list (TXT)
        txt_file = output_dir / f"articles_{year}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Health Insurance Literature - Year {year}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, article in enumerate(year_result["articles"], 1):
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
        
        # Save PMID list
        pmids_file = output_dir / f"pmids_{year}.txt"
        with open(pmids_file, 'w', encoding='utf-8') as f:
            for pmid in year_result["pmids"]:
                f.write(f"{pmid}\n")
        
        # Save APA references
        apa_file = output_dir / f"apa_references_{year}.txt"
        with open(apa_file, 'w', encoding='utf-8') as f:
            f.write(f"APA Reference List - Year {year}\n")
            f.write("=" * 50 + "\n\n")
            for i, article in enumerate(year_result["articles"], 1):
                apa_citation = APACitationGenerator.create_apa_citation(article)
                f.write(f"{i}. {apa_citation}\n\n")
        
        # Save statistics
        stats_file = output_dir / f"statistics_{year}.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"Health Insurance Literature Crawling Statistics - Year {year}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Query Condition: {year_result['query']}\n")
            f.write(f"Total Found Articles: {year_result['total_found']}\n")
            f.write(f"Target Count: {year_result['target_count']}\n")
            f.write(f"Actual Processed: {year_result['actual_processed']}\n")
            f.write(f"Successfully Parsed: {year_result['successful_articles']}\n")
            f.write(f"Successful Batches: {year_result.get('successful_batches', 'N/A')}\n")
            f.write(f"Failed Batches: {year_result.get('failed_batches', 'N/A')}\n")
            f.write(f"Crawling Time: {year_result['crawl_time']}\n")
            f.write(f"Execution Time: {year_result['execution_time_seconds']:.2f} seconds\n")
            if year_result['actual_processed'] > 0:
                f.write(f"Success Rate: {year_result['successful_articles']/year_result['actual_processed']*100:.1f}%\n")
            else:
                f.write(f"Success Rate: 0.0%\n")
        
        logger.info(f"Year {year} results saved to {output_dir}")
        logger.info(f"Year {year} file list:")
        logger.info(f"  - {json_file.name}")
        logger.info(f"  - {articles_file.name}")
        logger.info(f"  - {txt_file.name}")
        logger.info(f"  - {pmids_file.name}")
        logger.info(f"  - {apa_file.name}")
        logger.info(f"  - {stats_file.name}")
    
    def save_results(self, results: Dict):
        """
        Save overall results to base directory
        
        Args:
            results: Overall crawling results from all years
        """
        logger.info(f"Saving overall results to {self.base_output_dir}")
        
        # Save complete results (JSON)
        json_file = self.base_output_dir / "health_insurance_articles_all_years.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save article list (JSON)
        articles_file = self.base_output_dir / "articles_all_years.json"
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(results["articles"], f, ensure_ascii=False, indent=2)
        
        # Save article list (TXT)
        txt_file = self.base_output_dir / "articles_all_years.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Health Insurance Literature - All Years ({self.start_year}-{self.end_year})\n")
            f.write("=" * 60 + "\n\n")
            
            for i, article in enumerate(results["articles"], 1):
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
        
        # Save PMID list
        pmids_file = self.base_output_dir / "pmids_all_years.txt"
        with open(pmids_file, 'w', encoding='utf-8') as f:
            for pmid in results["pmids"]:
                f.write(f"{pmid}\n")
        
        # Save APA references
        apa_file = self.base_output_dir / "apa_references_all_years.txt"
        with open(apa_file, 'w', encoding='utf-8') as f:
            f.write(f"APA Reference List - All Years ({self.start_year}-{self.end_year})\n")
            f.write("=" * 60 + "\n\n")
            for i, article in enumerate(results["articles"], 1):
                apa_citation = APACitationGenerator.create_apa_citation(article)
                f.write(f"{i}. {apa_citation}\n\n")
        
        # Save overall statistics
        stats_file = self.base_output_dir / "statistics_all_years.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"Health Insurance Literature Crawling Statistics - All Years ({self.start_year}-{self.end_year})\n")
            f.write("=" * 70 + "\n")
            f.write(f"Query Condition: {results['query']}\n")
            f.write(f"Total Found Articles: {results['total_found']:,}\n")
            f.write(f"Target Count: {results['target_count']}\n")
            f.write(f"Actual Processed: {results['actual_processed']:,}\n")
            f.write(f"Successfully Parsed: {results['successful_articles']:,}\n")
            f.write(f"Successful Batches: {results.get('successful_batches', 'N/A')}\n")
            f.write(f"Failed Batches: {results.get('failed_batches', 'N/A')}\n")
            f.write(f"Crawling Time: {results['crawl_time']}\n")
            f.write(f"Execution Time: {results['execution_time_seconds']:.2f} seconds\n")
            if results['actual_processed'] > 0:
                f.write(f"Success Rate: {results['successful_articles']/results['actual_processed']*100:.1f}%\n")
            else:
                f.write(f"Success Rate: 0.0%\n")
            
            # Add year-by-year breakdown
            f.write(f"\nYear-by-Year Breakdown:\n")
            f.write("-" * 30 + "\n")
            for year in range(self.start_year, self.end_year + 1):
                if year in results.get('year_results', {}):
                    year_data = results['year_results'][year]
                    f.write(f"Year {year}: {year_data.get('successful_articles', 0):,} articles "
                           f"({year_data.get('total_found', 0):,} found, "
                           f"{year_data.get('actual_processed', 0):,} processed)\n")
                else:
                    f.write(f"Year {year}: No data available\n")
        
        # Save year summary
        summary_file = self.base_output_dir / "year_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Year Summary - Health Insurance Literature ({self.start_year}-{self.end_year})\n")
            f.write("=" * 60 + "\n\n")
            
            for year in range(self.start_year, self.end_year + 1):
                if year in results.get('year_results', {}):
                    year_data = results['year_results'][year]
                    f.write(f"Year {year}:\n")
                    f.write(f"  - Total Found: {year_data.get('total_found', 0):,}\n")
                    f.write(f"  - Processed: {year_data.get('actual_processed', 0):,}\n")
                    f.write(f"  - Successful: {year_data.get('successful_articles', 0):,}\n")
                    f.write(f"  - Success Rate: {year_data.get('successful_articles', 0)/max(year_data.get('actual_processed', 1), 1)*100:.1f}%\n")
                    f.write(f"  - Execution Time: {year_data.get('execution_time_seconds', 0):.2f} seconds\n")
                    f.write(f"  - Output Directory: year_{year}/\n\n")
                else:
                    f.write(f"Year {year}: No data available\n\n")
        
        logger.info(f"Overall results saved to {self.base_output_dir}")
        logger.info(f"Overall file list:")
        logger.info(f"  - {json_file.name}")
        logger.info(f"  - {articles_file.name}")
        logger.info(f"  - {txt_file.name}")
        logger.info(f"  - {pmids_file.name}")
        logger.info(f"  - {apa_file.name}")
        logger.info(f"  - {stats_file.name}")
        logger.info(f"  - {summary_file.name}")

def main():
    """Main function"""
    logger.info("=== MeSH Health Insurance Literature Crawler Started ===")
    
    try:
        # Check configuration
        Config.validate_config()
        
        # Create crawler instance
        crawler = MeSHHealthInsuranceCrawler()
        
        # Execute crawling
        results = crawler.crawl_health_insurance_articles()
        
        if results:
            # Save results
            crawler.save_results(results)
            
            # Display statistics
            print("\n=== Overall Crawling Statistics ===")
            print(f"Year Range: {crawler.start_year}-{crawler.end_year}")
            print(f"Total Found Articles: {results['total_found']:,}")
            print(f"Target Count: {results['target_count']}")
            print(f"Actual Processed: {results['actual_processed']:,}")
            print(f"Successfully Parsed: {results['successful_articles']:,}")
            print(f"Successful Batches: {results.get('successful_batches', 'N/A')}")
            print(f"Failed Batches: {results.get('failed_batches', 'N/A')}")
            if results['actual_processed'] > 0:
                print(f"Success Rate: {results['successful_articles']/results['actual_processed']*100:.1f}%")
            else:
                print(f"Success Rate: 0.0%")
            print(f"Execution Time: {results['execution_time_seconds']:.2f} seconds")
            
            # Display year-by-year breakdown
            print(f"\n=== Year-by-Year Breakdown ===")
            for year in range(crawler.start_year, crawler.end_year + 1):
                if year in results.get('year_results', {}):
                    year_data = results['year_results'][year]
                    print(f"Year {year}: {year_data.get('successful_articles', 0):,} articles "
                          f"({year_data.get('total_found', 0):,} found, "
                          f"{year_data.get('actual_processed', 0):,} processed)")
                else:
                    print(f"Year {year}: No data available")
            
            print(f"\n=== Output Structure ===")
            print(f"Base Directory: {crawler.base_output_dir}")
            print(f"Individual year folders: year_2020/, year_2021/, etc.")
            print(f"Overall results: articles_all_years.json, statistics_all_years.txt, etc.")
            
        else:
            logger.error("Crawling failed, no results obtained")
            
    except Exception as e:
        logger.error(f"Error occurred during execution: {e}")
        raise
    
    logger.info("=== Crawling Completed ===")

if __name__ == "__main__":
    main() 