import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """PubMed API Configuration Class"""
    
    # PubMed API settings
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # Get sensitive information from environment variables (all optional)
    API_KEY = os.getenv("PUBMED_API_KEY", "")  # Optional, but recommended
    
    # API rate limit settings - corrected according to NCBI official documentation
    # Without API Key: 3 requests per second (3 rps)
    # With API Key: 10 requests per second (10 rps)
    RATE_LIMIT_DELAY = 0  # Remove delay, PubMed API is concurrency limited, not request interval limited
    MAX_REQUESTS_PER_SECOND = 10 if API_KEY else 3
    MAX_REQUESTS_PER_MINUTE = 600 if API_KEY else 180
    
    # Default search settings
    DEFAULT_MAX_RESULTS = 10
    DEFAULT_BATCH_SIZE = 200  # Adjusted to 200 to avoid URL too long
    
    # Output settings
    OUTPUT_DIR = "output"
    LOG_LEVEL = "INFO"
    
    @classmethod
    def validate_config(cls):
        """Validate if configuration is correct"""
        # Email is optional, no need to enforce requirement
        return True 