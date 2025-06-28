import xml.etree.ElementTree as ET
import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PubMedDataParser:
    """PubMed Data Parser"""
    
    @staticmethod
    def parse_xml_abstracts(xml_data: str) -> List[Dict]:
        """
        Parse XML format abstract data, merge all abstract paragraphs, and add full_abstract field
        """
        try:
            root = ET.fromstring(xml_data)
            articles = []
            for article in root.findall(".//PubmedArticle"):
                try:
                    pmid_elem = article.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else ""
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else ""
                    # Abstract paragraph merging
                    abstract_elem = article.find(".//Abstract")
                    abstract_texts = []
                    if abstract_elem is not None:
                        for ab in abstract_elem.findall("AbstractText"):
                            label = ab.attrib.get('Label', '')
                            text = ab.text or ""
                            if text.strip():
                                if label:
                                    abstract_texts.append(f"[{label}] {text}")
                                else:
                                    abstract_texts.append(text)
                        if not abstract_texts:
                            general_abstract = abstract_elem.findtext("AbstractText", default="")
                            if general_abstract:
                                abstract_texts.append(general_abstract)
                    if not abstract_texts:
                        other_abstract = article.findtext(".//AbstractText", default="")
                        if other_abstract:
                            abstract_texts.append(other_abstract)
                    # Merge all paragraphs and clean up
                    full_abstract = " ".join(abstract_texts).strip()
                    
                    # Authors - improved parsing
                    authors = []
                    author_list = article.findall(".//Author")
                    for author in author_list:
                        last_name_elem = author.find("LastName")
                        first_name_elem = author.find("ForeName")
                        initials_elem = author.find("Initials")
                        
                        last_name = last_name_elem.text if last_name_elem is not None else ""
                        first_name = first_name_elem.text if first_name_elem is not None else ""
                        initials = initials_elem.text if initials_elem is not None else ""
                        
                        # Build author name
                        if last_name and first_name:
                            authors.append(f"{first_name} {last_name}".strip())
                        elif last_name and initials:
                            authors.append(f"{initials} {last_name}".strip())
                        elif last_name:
                            authors.append(last_name.strip())
                        elif first_name:
                            authors.append(first_name.strip())
                    
                    # Journal - ensure proper case
                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else ""
                    # Title case for journal names
                    if journal:
                        journal = journal.title()
                    # Publication date
                    pub_date_elem = article.find(".//PubDate")
                    pub_date = ""
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find("Year")
                        month_elem = pub_date_elem.find("Month")
                        day_elem = pub_date_elem.find("Day")
                        year = year_elem.text if year_elem is not None else ""
                        month = month_elem.text if month_elem is not None else ""
                        day = day_elem.text if day_elem is not None else ""
                        if year and month:
                            if day:
                                pub_date = f"{year}-{month}-{day}"
                            else:
                                pub_date = f"{year}-{month}"
                        else:
                            pub_date = year
                    # MeSH Terms
                    mesh_terms = [mh.text for mh in article.findall(".//MeshHeading/DescriptorName") if mh.text]
                    # Publication type
                    pub_types = [pt.text for pt in article.findall(".//PublicationType") if pt.text]
                    # DOI
                    doi = article.findtext(".//ELocationID[@EIdType='doi']", default="")
                    # Volume and Issue
                    volume_elem = article.find(".//Volume")
                    volume = volume_elem.text if volume_elem is not None else ""
                    issue_elem = article.find(".//Issue")
                    issue = issue_elem.text if issue_elem is not None else ""
                    # Pages
                    pages_elem = article.find(".//MedlinePgn")
                    pages = pages_elem.text if pages_elem is not None else ""
                    
                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": full_abstract,  # Keep old field name for compatibility
                        "full_abstract": full_abstract,
                        "abstract_paragraphs": abstract_texts,
                        "authors": authors,
                        "journal": journal,
                        "pub_date": pub_date,
                        "mesh_terms": mesh_terms,
                        "pub_types": pub_types,
                        "doi": doi,
                        "volume": volume,
                        "issue": issue,
                        "pages": pages
                    })
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue
            logger.info(f"Successfully parsed {len(articles)} articles")
            return articles
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during parsing: {e}")
            raise
    
    @staticmethod
    def parse_abstract_text(abstract_text: str) -> List[Dict]:
        """
        Parse plain text format abstracts
        
        Args:
            abstract_text: Abstract text
            
        Returns:
            Simplified article information list
        """
        articles = []
        lines = abstract_text.strip().split('\n')
        
        current_article = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple parsing logic, can be adjusted based on actual format
            if line.startswith('PMID-'):
                if current_article:
                    articles.append(current_article)
                current_article = {"pmid": line[5:].strip()}
            elif line.startswith('TI  -'):
                current_article["title"] = line[5:].strip()
            elif line.startswith('AB  -'):
                current_article["abstract"] = line[5:].strip()
        
        # Add the last article
        if current_article:
            articles.append(current_article)
        
        return articles

class APACitationGenerator:
    """APA Citation Generator"""
    
    @staticmethod
    def create_apa_citation(article: Dict) -> str:
        """
        Create APA format citation from article data
        
        Args:
            article: Article dictionary
            
        Returns:
            APA format citation string
        """
        try:
            # Extract and format authors
            authors = article.get('authors', [])
            if authors:
                author_names = []
                for author in authors:
                    if author:
                        # Handle Chinese names and other formats
                        parts = author.split()
                        if len(parts) >= 2:
                            # For Chinese names, the last part is usually the surname
                            last_name = parts[-1]
                            first_initial = parts[0][0] + "."
                            author_names.append(f"{last_name}, {first_initial}")
                        else:
                            # Handle single name case
                            author_names.append(author)
                
                # Format author string according to APA rules
                if len(author_names) == 1:
                    authors_str = author_names[0]
                elif len(author_names) == 2:
                    authors_str = f"{author_names[0]} & {author_names[1]}"
                else:
                    authors_str = ", ".join(author_names[:-1]) + f", & {author_names[-1]}"
            else:
                authors_str = "Unknown Author"
            
            # Extract title
            title = article.get('title', 'Unknown Title')
            if title.endswith('.'):
                title = title[:-1]  # Remove trailing period
            
            # Extract journal information
            journal = article.get('journal', 'Unknown Journal')
            volume = article.get('volume', '')
            issue = article.get('issue', '')
            pages = article.get('pages', '')
            
            # Extract and format publication date
            pub_date = article.get('pub_date', '')
            if pub_date:
                try:
                    # Parse date (format: "2025-06-25" or "2025-Jun-25")
                    if '-' in pub_date:
                        parts = pub_date.split('-')
                        if len(parts) >= 2:
                            year = parts[0]
                            month = parts[1]
                            # Convert month abbreviation to full name
                            month_map = {
                                '01': 'January', '02': 'February', '03': 'March', '04': 'April',
                                '05': 'May', '06': 'June', '07': 'July', '08': 'August',
                                '09': 'September', '10': 'October', '11': 'November', '12': 'December',
                                'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
                                'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
                                'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
                            }
                            month_full = month_map.get(month, month)
                            if len(parts) > 2:
                                date_str = f"{year}, {month_full} {parts[2]}"
                            else:
                                date_str = f"{year}, {month_full}"
                        else:
                            date_str = pub_date
                    else:
                        date_str = pub_date
                except:
                    date_str = pub_date
            else:
                date_str = "Unknown Date"
            
            # Extract DOI
            doi = article.get('doi', '')
            
            # Construct APA citation
            apa = f"{authors_str}. ({date_str}). {title}. {journal}"
            
            if volume:
                apa += f", {volume}"
                if issue:
                    apa += f"({issue})"
            
            if pages:
                apa += f", {pages}"
            
            apa += "."
            
            if doi:
                apa += f" https://doi.org/{doi}"
            
            return apa
            
        except Exception as e:
            return f"Error creating APA citation: {e}"
    
    @staticmethod
    def create_apa_reference_list(articles: List[Dict]) -> List[str]:
        """
        Create APA reference list for multiple articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of APA format citations
        """
        references = []
        for article in articles:
            apa_citation = APACitationGenerator.create_apa_citation(article)
            references.append(apa_citation)
        return references

class FileHandler:
    """File handling utility class"""
    
    # Dictionary for caching query directories
    _query_dirs = {}
    
    @staticmethod
    def _create_query_dir(query: str = None, output_dir: str = "output") -> str:
        """
        Create new directory for query, return existing directory if already exists
        
        Args:
            query: Query string
            output_dir: Base output directory
            
        Returns:
            Directory path
        """
        # Check if directory for this query already exists
        cache_key = f"{output_dir}:{query}"
        if cache_key in FileHandler._query_dirs:
            return FileHandler._query_dirs[cache_key]
        
        # Ensure base output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate directory name from query string
        if query:
            # Clean query string, remove invalid characters
            query_part = "".join(c if c.isalnum() else "_" for c in query)
            query_part = query_part[:50]  # Limit length
            dir_name = f"{timestamp}_{query_part}"
        else:
            dir_name = timestamp
            
        # Create complete path
        query_dir = os.path.join(output_dir, dir_name)
        os.makedirs(query_dir, exist_ok=True)
        
        # Cache directory path
        FileHandler._query_dirs[cache_key] = query_dir
        
        return query_dir
    
    @staticmethod
    def save_to_json(data: List[Dict], filename: str, output_dir: str = "output", query: str = None):
        """
        Save data as JSON file
        
        Args:
            data: Data to save
            filename: File name
            output_dir: Output directory
            query: Query string, used to create subdirectory
        """
        # Create new directory for this query
        query_dir = FileHandler._create_query_dir(query, output_dir)
        
        filepath = os.path.join(query_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to JSON: {filepath}")
        return filepath
    
    @staticmethod
    def save_to_txt(data: List[Dict], filename: str, output_dir: str = "output", query: str = None):
        """
        Save data as TXT file
        
        Args:
            data: Data to save
            filename: File name
            output_dir: Output directory
            query: Query string, used to create subdirectory
        """
        # Create new directory for this query
        query_dir = FileHandler._create_query_dir(query, output_dir)
        
        filepath = os.path.join(query_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, item in enumerate(data, 1):
                f.write(f"=== Item {i} ===\n")
                for key, value in item.items():
                    if isinstance(value, list):
                        f.write(f"{key}: {', '.join(value)}\n")
                    else:
                        f.write(f"{key}: {value}\n")
                f.write("\n" + "="*50 + "\n\n")
        
        logger.info(f"Data saved to TXT: {filepath}")
        return filepath
    
    @staticmethod
    def save_raw_data(data: str, filename: str, output_dir: str = "output", query: str = None):
        """
        Save raw data as file
        
        Args:
            data: Raw data string
            filename: File name
            output_dir: Output directory
            query: Query string, used to create subdirectory
        """
        # Create new directory for this query
        query_dir = FileHandler._create_query_dir(query, output_dir)
        
        filepath = os.path.join(query_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        
        logger.info(f"Raw data saved: {filepath}")
        return filepath
    
    @staticmethod
    def save_apa_references(articles: List[Dict], filename: str = "apa_references.txt", 
                           output_dir: str = "output", query: str = None):
        """
        Save APA format references
        
        Args:
            articles: List of article dictionaries
            filename: Output filename
            output_dir: Output directory
            query: Query string, used to create subdirectory
        """
        # Create new directory for this query
        query_dir = FileHandler._create_query_dir(query, output_dir)
        
        filepath = os.path.join(query_dir, filename)
        
        # Generate APA references
        references = APACitationGenerator.create_apa_reference_list(articles)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("APA Reference List\n")
            f.write("=" * 50 + "\n\n")
            for i, ref in enumerate(references, 1):
                f.write(f"{i}. {ref}\n\n")
        
        logger.info(f"APA references saved: {filepath}")
        return filepath

class QueryBuilder:
    """Query building utility class"""
    
    @staticmethod
    def build_advanced_query(terms: List[str], 
                           authors: List[str] = None,
                           date_range: tuple = None,
                           journal: str = None) -> str:
        """
        Build advanced query string
        
        Args:
            terms: Search terms
            authors: Author names
            date_range: Date range tuple (start_year, end_year)
            journal: Journal name
            
        Returns:
            Query string
        """
        query_parts = []
        
        # Add search terms
        if terms:
            terms_query = " OR ".join([f'"{term}"[MeSH Terms]' for term in terms])
            query_parts.append(f"({terms_query})")
        
        # Add authors
        if authors:
            authors_query = " OR ".join([f'"{author}"[Author]' for author in authors])
            query_parts.append(f"({authors_query})")
        
        # Add date range
        if date_range:
            start_year, end_year = date_range
            query_parts.append(f'"{start_year}:{end_year}"[Date - Publication]')
        
        # Add journal
        if journal:
            query_parts.append(f'"{journal}"[Journal]')
        
        # Combine with AND
        query = " AND ".join(query_parts)
        
        # Add common filters
        query += " AND hasabstract AND \"English\"[Language]"
        
        return query
    
    @staticmethod
    def build_boolean_query(terms: List[str], 
                          operator: str = "AND") -> str:
        """
        Build boolean query string
        
        Args:
            terms: Search terms
            operator: Boolean operator (AND, OR, NOT)
            
        Returns:
            Query string
        """
        return f" {operator} ".join(terms) 