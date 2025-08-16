# cow-stuffz

The platform unifies fragmented registries into a scalable graph-relational datastore, vectorizing symbolic identifiers into a searchable ontology for ultra-fast cross-jurisdiction queries. A blockchain-adjacent audit layer secures immutable lineage, evolving simple marks into a next-gen asset knowledge graph.

---

# Texas Brand Scraper

A Python-based web scraper for extracting brand records from Fort Bend County, Texas public records.

## Features

- **Automated Brand Record Extraction**: Scrapes brand-related documents from the Fort Bend County website
- **Multiple Output Formats**: Exports data to both CSV and JSONL formats
- **Headless Browser Automation**: Uses Playwright for reliable web scraping
- **Error Handling**: Robust error handling and timeout management
- **Configurable**: Easy to modify for different document types or counties

## Project Structure

```
texas_brand_scraper/
├── scrape_texas_brands_FortBendCounty.py  # Main scraping script
├── requirements.txt                        # Python dependencies
├── fort_bend_brands.csv                   # Output CSV file
├── fort_bend_brands.jsonl                 # Output JSONL file
└── README.md                              # This file
```

## Prerequisites

- Python 3.7+
- pip3
- Internet connection

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd texas_brand_scraper
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   python3 -m playwright install
   ```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python3 scrape_texas_brands_FortBendCounty.py
```

### What It Does

1. **Navigates** to the Fort Bend County search page
2. **Selects** "BRAND" as the document type
3. **Submits** the search form
4. **Waits** for results to load
5. **Scrapes** the results table
6. **Exports** data to CSV and JSONL files

### Output Files

- `fort_bend_brands.csv`: Structured data in CSV format
- `fort_bend_brands.jsonl`: JSON Lines format for easy processing

### Data Fields

Each record includes:
- Instrument Number
- Date
- Document Type
- Grantor
- Grantee
- Legal Description
- Raw data from all table columns

## Configuration

You can modify the following constants in the script:

```python
SEARCH_ENTRY_URL = "https://ccweb.co.fort-bend.tx.us/RealEstate/SearchEntry.aspx"
SEARCH_RESULTS_URL = "https://ccweb.co.fort-bend.tx.us/RealEstate/SearchResults.aspx"
BRAND_CHECKBOX_ID = "#cphNoMargin_f_dclDocType_14"
OUTPUT_CSV = "fort_bend_brands.csv"
OUTPUT_JSONL = "fort_bend_brands.jsonl"
```

## Dependencies

- **playwright**: Web automation and scraping
- **pandas**: Data manipulation (optional, for future enhancements)
- **sqlalchemy**: Database operations (optional, for future enhancements)

## Troubleshooting

### Common Issues

1. **"BRAND checkbox not found"**: The website structure may have changed
2. **Timeout errors**: Increase timeout values in the script
3. **No results**: Check if the website is accessible and search criteria

### Debug Mode

The script runs with `headless=False` by default, so you can see the browser in action. Set to `True` for production use.

## Legal and Ethical Considerations

- **Respect robots.txt**: Check the website's robots.txt file
- **Rate limiting**: The script includes delays to be respectful
- **Terms of Service**: Ensure compliance with the website's terms
- **Public Data Only**: Only scrape publicly available information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with all applicable laws and website terms of service.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

## Future Enhancements

- [ ] Support for other Texas counties
- [ ] Database integration
- [ ] Web interface
- [ ] Scheduled scraping
- [ ] Additional document types
- [ ] Data validation and cleaning
- [ ] Convert brand and mark to 8 or 16 bit for fast search
