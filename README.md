# PubMed Health Insurance Literature Crawler

A Python tool for crawling health insurance related literature from PubMed using MeSH (Medical Subject Headings) queries. This tool efficiently retrieves and processes large amounts of biomedical literature data with support for multiple output formats including APA citations.

## Features

- **MeSH-based Querying**: Uses precise MeSH vocabulary for accurate literature retrieval
- **Batch Processing**: Efficiently handles large datasets (target: 10,000+ articles)
- **Multiple Output Formats**: JSON, TXT, and APA citation formats
- **Comprehensive Data Extraction**: Includes abstracts, authors, journals, dates, DOIs, and MeSH terms
- **APA Citation Generation**: Directly generates APA format from parsed XML data (not via RIS)
- **Integrated Testing**: One-click test for all major functions
- **Robust Error Handling**: Logs errors and progress

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pubmed-health-insurance-crawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Configure PubMed API key in `.env` or `config.py` for higher rate limits.

## Configuration

Edit `config.py` to adjust:
- API base URL and key
- Batch size and limits

## Usage

### Run the main crawler
```bash
python mesh_health_insurance_crawler.py
```

### Run integrated tests
```bash
python test_integrated_system.py
```

## Output Formats

All output files are saved in a timestamped directory under `output/` (ignored by git):

- `health_insurance_articles.json` — Full structured data
- `articles.json` — Article list only
- `articles.txt` — Human-readable text
- `pmids.txt` — PMID list
- `apa_references.txt` — APA citation list (generated directly from XML data)
- `statistics.txt` — Summary statistics

### Example: APA Citation Output
```
APA Reference List
==================================================
1. Smith, J., Doe, J., & Johnson, A. (2023, June 15). Health Insurance Coverage and Access to Care. Journal of Health Policy, 15(3), 245-260. https://doi.org/10.1007/s12345-023-01234-5
```

## Project Structure
```
├── mesh_health_insurance_crawler.py  # Main crawler script
├── utils.py                          # Utilities (XML parsing, APA generator)
├── config.py                         # Configuration
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── test_integrated_system.py         # Integrated test script
├── .gitignore                        # Ignore rules
```

## Notes
- All APA citations are generated directly from parsed PubMed XML data, not via RIS or other formats.
- All output and log files are ignored by git by default.
- For best results, use a PubMed API key (see NCBI documentation).

## License
MIT License

## Support
If you have questions or issues, please open an issue in the repository. 