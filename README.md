# Safespill Hangar Projects Scraper

A comprehensive web scraping tool designed to collect information about upcoming aircraft Maintenance, Repair, and Overhaul (MRO) hangar construction and retrofit projects from Bing News and Google News. This tool supports Safespill's international sales team by providing timely market intelligence.

## Features

- **Dual Regional Support**: Separate scrapers for UK + North America and EMEA regions
- **Multi-Source News**: Collects data from both Google News and Bing News APIs
- **Smart Filtering**: Excludes museums, historic aircraft, air shows, and unrelated content
- **Excel Output**: Generates formatted Excel files with clickable hyperlinks
- **Email Automation**: Sends weekly reports via email with professional formatting
- **Duplicate Prevention**: Tracks existing articles to avoid duplicates
- **Scheduled Execution**: Automated weekly runs every Monday at 8:00 AM CT
- **Initial Backfill**: 12-month historical data collection for new deployments

## Project Structure

```
safespill_scraping/
├── main.py              # Main execution script
├── config.py            # Configuration management
├── news_scraper.py      # News API integration and filtering
├── excel_handler.py     # Excel file operations
├── email_sender.py      # Email functionality
├── scheduler.py         # Automated scheduling
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables template
├── README.md           # This file
├── reports/            # Generated Excel reports
│   ├── UK_NA_hangar_projects.xlsx
│   └── EMEA_hangar_projects.xlsx
└── data/               # Data storage (if needed)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- SerpAPI account and API key
- Email account for sending reports (optional)

### Setup Instructions

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your actual values
   ```

4. **Required Configuration**:
   - `SERPAPI_KEY`: Your SerpAPI key (get from https://serpapi.com/)
   
5. **Optional Email Configuration**:
   - `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
   - `SMTP_PORT`: SMTP port (default: 587)
   - `EMAIL_USER`: Your email address
   - `EMAIL_PASSWORD`: Your email password or app password
   - `RECIPIENT_EMAILS`: Comma-separated list of recipient emails

## Usage

### Command Line Options

```bash
# Run initial 12-month backfill
python main.py backfill

# Run weekly scraping
python main.py weekly

# Test configuration
python main.py test

# Start automated scheduler
python main.py schedule

# Run for specific region
python main.py region uk_na
python main.py region emea

# Run weekly scraping (default)
python main.py
```

### Initial Setup

1. **Test Configuration**:
   ```bash
   python main.py test
   ```

2. **Run Initial Backfill** (collects 12 months of historical data):
   ```bash
   python main.py backfill
   ```

3. **Start Automated Scheduling**:
   ```bash
   python main.py schedule
   ```

### Manual Execution

For manual runs or testing:

```bash
# Run weekly scraping for all regions
python main.py weekly

# Run for specific region only
python main.py region uk_na
```

## Excel Output Format

Each Excel file contains the following columns:

| Column | Description |
|--------|-------------|
| Project Title | Name or description of the hangar project |
| Source URL | Direct link to the news article (clickable hyperlink) |
| Summary | Brief description of the project |
| Country/Region | Specific country or region where the project is located |
| Language | Language of the source article |
| Date Published | When the article was published |
| Week Collected | When this information was gathered |

## Email Reports

When email is configured, the system sends professional HTML-formatted emails containing:

- Report summary with article count
- Region-specific information
- Description of included content
- Excel file attachment
- Professional Safespill branding

## Search Queries

The scraper uses the following search queries for each region:

- Aircraft MRO hangar construction
- Aircraft maintenance hangar retrofit
- MRO facility expansion
- Aircraft hangar renovation
- Aviation maintenance facility

## Filtering Logic

The system automatically filters out articles containing:
- Museum, historic, vintage, classic, antique
- Exhibition, display, showcase, tourist
- Air show, airshow, festival, celebration
- Memorial, tribute, heritage, legacy

## Regional Coverage

### UK + North America (uk_na)
- **Countries**: United States, Canada, United Kingdom
- **News Sources**: Google News (US), Bing News (US)
- **Output File**: `UK_NA_hangar_projects.xlsx`

### EMEA (Europe, Middle East, Africa)
- **Countries**: Germany, France, Italy, Spain, Netherlands, Belgium, Switzerland, Austria, Poland, Czech Republic, Hungary, Romania, Bulgaria, Croatia, Slovenia, Slovakia, Estonia, Latvia, Lithuania, Finland, Sweden, Norway, Denmark, Iceland, Ireland, United Arab Emirates, Saudi Arabia, Qatar, Kuwait, Bahrain, Oman, Jordan, Lebanon, Israel, Turkey, Egypt, Morocco, Algeria, Tunisia, Libya, South Africa, Nigeria, Kenya, Ethiopia, Ghana, Uganda, Tanzania
- **News Sources**: Google News (Germany), Bing News (Germany)
- **Output File**: `EMEA_hangar_projects.xlsx`

## Scheduling

The system is configured to run automatically every Monday at 8:00 AM Central Time. To modify the schedule, edit the `SCHEDULE_TIME` and `SCHEDULE_DAY` variables in `config.py`.

## Logging

All operations are logged to both console and `scraper.log` file with detailed information about:
- Scraping progress
- Article counts
- File operations
- Email sending status
- Error messages

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your SerpAPI key is correctly set in the `.env` file
2. **Email Not Sending**: Check SMTP settings and ensure 2FA is properly configured for Gmail
3. **No Articles Found**: Verify internet connection and API quota
4. **Excel File Errors**: Ensure write permissions in the reports directory

### Testing

Use the test command to verify configuration:
```bash
python main.py test
```

This will check:
- API key validity
- Email configuration
- File path accessibility
- Basic functionality

## API Usage

The tool uses SerpAPI for accessing Google News and Bing News. Each search query consumes API credits. Monitor your usage at https://serpapi.com/dashboard.

## Support

For technical support or questions about the scraping tool, contact your IT department or the development team.

## License

This tool is developed specifically for Safespill's internal use. Please ensure compliance with all applicable terms of service for the APIs used. 