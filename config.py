import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS', '').split(',')
    
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
            'google_news': {'gl': 'us', 'hl': 'en'},
            'bing_news': {'cc': 'us'},
            'countries': ['United States', 'Canada', 'United Kingdom']
        },
        'emea': {
            'google_news': {'gl': 'de', 'hl': 'en'},
            'bing_news': {'cc': 'de'},
            'countries': ['Germany', 'France', 'Italy', 'Spain', 'Netherlands', 
                         'Belgium', 'Switzerland', 'Austria', 'Poland', 'Czech Republic',
                         'Hungary', 'Romania', 'Bulgaria', 'Croatia', 'Slovenia',
                         'Slovakia', 'Estonia', 'Latvia', 'Lithuania', 'Finland',
                         'Sweden', 'Norway', 'Denmark', 'Iceland', 'Ireland',
                         'United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Kuwait',
                         'Bahrain', 'Oman', 'Jordan', 'Lebanon', 'Israel', 'Turkey',
                         'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Libya', 'South Africa',
                         'Nigeria', 'Kenya', 'Ethiopia', 'Ghana', 'Uganda', 'Tanzania']
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
        'Country/Region',
        'Language',
        'Date Published',
        'Week Collected'
    ]
    
    # Scheduling
    SCHEDULE_TIME = '08:00'  # 8:00 AM CT
    SCHEDULE_DAY = 'monday'
    
    # Search Parameters
    MAX_RESULTS_PER_QUERY = 10
    BACKFILL_MONTHS = 12 