import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Search Configuration
    SEARCH_QUERIES = [
            # 'aircraft MRO hangar construction maintenance'
            'aircraft MRO hangar construction',
            'aircraft maintenance hangar retrofit',
            'MRO facility expansion',
            'aircraft hangar renovation',
            'aviation maintenance facility'
        ]
    
    # Regional Settings
    REGIONS = {
        'uk_na': {
            'additional_queries': [ 'United States', 'United Kingdom', 'Canada'],
            # 'google_news': {'gl': 'us', 'hl': 'en'},
            # 'bing_news': {'cc': 'us'},
            'countries': ['United States', 'Canada', 'United Kingdom'],
            'recipient_emails': ["tristanm@safespill.com", "samb@safespill.com"]
        },
        'emea': {
            'additional_queries': ['Europe', 'Middle East', 'Africa'],
            # 'google_news': {'gl': 'de', 'hl': 'en'},
            # 'bing_news': {'cc': 'de'},
            'countries': ['Germany', 'France', 'Italy', 'Spain', 'Netherlands', 
                         'Belgium', 'Switzerland', 'Austria', 'Poland', 'Czech Republic',
                         'Hungary', 'Romania', 'Bulgaria', 'Croatia', 'Slovenia',
                         'Slovakia', 'Estonia', 'Latvia', 'Lithuania', 'Finland',
                         'Sweden', 'Norway', 'Denmark', 'Iceland', 'Ireland',
                         'United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Kuwait',
                         'Bahrain', 'Oman', 'Jordan', 'Lebanon', 'Israel', 'Turkey',
                         'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Libya', 'South Africa',
                         'Nigeria', 'Kenya', 'Ethiopia', 'Ghana', 'Uganda', 'Tanzania'],
            'recipient_emails': ["tristanm@safespill.com", "rogerb@safespill.com"]
        }
    }
    
    # File Paths
    REPORTS_DIR = 'reports'
    DATA_DIR = 'data'
    
    # Excel Configuration
    EXCEL_FIELDS = [
        'Project Title',
        'Source URL', 
        'Summary',
        'Date Published',
        "Region",
        "Country",
        "patterns",
        # "Is Hangar Related",
        # "Completion Status",
        'Week Collected'
    ]
    
    # Scheduling
    SCHEDULE_TIME = '08:00'  # 8:00 AM CT
    SCHEDULE_DAY = 'monday'
    
    # Search Parameters
    MAX_RESULTS_PER_QUERY = 10
    BACKFILL_MONTHS = 12 