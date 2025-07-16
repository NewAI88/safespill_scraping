import json
from colorlog import ColoredFormatter

# Configure colorful logging using Rich
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
from config import Config

# Configure logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("color_logger")
# logger.setLevel(logging.DEBUG)

# Clear existing handlers to avoid duplicate logs
if logger.hasHandlers():
    logger.handlers.clear()


# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Define color format
formatter = ColoredFormatter(
    "%(log_color)s[%(levelname)s]%(reset)s %(message_log_color)s%(message)s",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={
        'message': {
            'DEBUG':    'white',
            'INFO':     'bold_green',
            'WARNING':  'bold_yellow',
            'ERROR':    'bold_red',
            'CRITICAL': 'bold_red',
        }
    },
    style='%'
)

# Apply formatter to handler
ch.setFormatter(formatter)
logger.addHandler(ch)

class NewsScraper:
    def __init__(self, region: str):
        self.region = region
        self.config = Config()
        self.api_key = self.config.SERPAPI_KEY
        
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found in environment variables")
    
    def search_google_news(self, query: str, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Search Google News for MRO hangar projects"""
        try:
            params = {
                "engine": "google_news",
                "q": query,
                "api_key": self.api_key,
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "news_results" in results:
                return self._filter_mro_articles(results["news_results"], start_date)
            else:
                if "error" in results:
                    logger.error(f"Error in search results for query '{query}': {results['error']}")
                else:
                    logger.warning(f"No news results found for query: {query}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Google News for query '{query}': {str(e)}")
            return []

    def _check_date(self, date_str: str, is_backfill: bool) -> bool:
        """Check if the Bing News date string is valid for the current mode (backfill or weekly)"""
        if not date_str:
            logger.warning("Empty date string provided")
            return False
        try:
            if date_str.endswith('m'):
                return True
            if date_str.endswith('h'):
                return True
            elif date_str.endswith('d'):
                if is_backfill:
                    return True
                else:
                    days = int(date_str[:-1])
                    if days < 8:
                        return True
                    return False
            elif date_str.endswith('mon') and is_backfill:
                return True
            elif date_str.endswith('y') and is_backfill:
                years = int(date_str[:-1])
                if years < 2:
                    return True
            return False
        except Exception:
            return False

    def search_bing_news(self, query: str, is_backfill: bool = False) -> List[Dict[str, Any]]:
        """Search Bing News for MRO hangar projects with pagination and date range check"""
        try:
            params = {
                "engine": "bing_news",
                "q": query,
                "api_key": self.api_key,
                "count": self.config.MAX_RESULTS_PER_QUERY
            }
            if is_backfill:
                params['qft'] = 'sortbydate="1"'
            else:
                params['qft'] = 'interval="8"+sortbydate="1"'

            all_articles = []
            first = 1
            stop_paging = False
            while not stop_paging:
                params['first'] = first
                search = GoogleSearch(params)
                results = search.get_dict()
                organic_results = results.get("organic_results", [])
                if not organic_results:
                    break
                for article in organic_results:
                    date_str = article.get('date', '')
                    is_valid_date = self._check_date(date_str, is_backfill)
                    if not is_valid_date:
                        stop_paging = True
                        break
                    all_articles.append(article)
                if stop_paging or len(organic_results) < params['count']:
                    break
                first += params['count']
            return self._filter_mro_articles(all_articles)
        except Exception as e:
            logger.error(f"Error searching Bing News for query '{query}': {str(e)}")
            return []
    
    def _filter_mro_articles(self, articles: List[Dict[str, Any]], start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Filter articles to only include MRO hangar projects, excluding museums and unrelated content"""
        filtered_articles = []
        
        # Keywords to exclude
        exclude_keywords = [
            'museum', 'historic', 'vintage', 'classic', 'antique', 'restoration',
            'exhibition', 'display', 'showcase', 'tourist', 'visitor center',
            'air show', 'airshow', 'festival', 'celebration', 'anniversary',
            'memorial', 'tribute', 'heritage', 'legacy', 'preservation'
        ]
        
        # Keywords that indicate MRO projects
        mro_keywords = [
            'mro', 'maintenance', 'repair', 'overhaul', 'facility', 'hangar',
            'construction', 'expansion', 'renovation', 'retrofit', 'upgrade',
            'modernization', 'development', 'project', 'investment', 'contract'
        ]
        
        for article in articles:
            title = article.get('title', '').lower()
            snippet = article.get('snippet', '').lower()
            content = f"{title} {snippet}"
            
            # Check for exclusion keywords
            if any(keyword in content for keyword in exclude_keywords):
                continue
            
            # Check for MRO-related keywords
            if any(keyword in content for keyword in mro_keywords):
                # Filter by date if start_date is provided
                if start_date:
                    date_str = article.get('date', '')
                    if date_str:
                        try:
                            # Parse the date from the article
                            article_date = self._parse_article_date(date_str)
                            if article_date and article_date >= start_date:
                                filtered_articles.append(article)
                        except Exception:
                            # If date parsing fails, include the article
                            filtered_articles.append(article)
                else:
                    filtered_articles.append(article)
        
        return filtered_articles
    
    def scrape_all_sources(self, is_backfill: bool = False) -> List[Dict[str, Any]]:
        """Scrape all news sources for the region"""
        all_articles = []
        start_date = None
        
        if is_backfill:
            start_date = datetime.now() - timedelta(days=365)
        
        queries = self.config.SEARCH_QUERIES
        for query in queries:
            for additional_query in self.config.REGIONS[self.region].get('additional_queries', []):
                real_query = f"{query} {additional_query}"
                logger.info(f"Searching for query: {real_query}")

                # Search Google News
                google_results = self.search_google_news(real_query, start_date)
                all_articles.extend(google_results)

                # Search Bing News
                bing_results = self.search_bing_news(real_query, is_backfill=is_backfill)
                all_articles.extend(bing_results)
        # Remove duplicates based on URL
        unique_articles = self._remove_duplicates(all_articles)
        logger.info(f"Found {len(unique_articles)} unique articles for {self.region}")
        return unique_articles
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    def process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format articles for Excel output"""
        processed_articles = []
        now = datetime.now()
        iso_year, iso_week, _ = now.isocalendar()
        current_week = f"{iso_year}-W{iso_week:02d}"
        
        for article in articles:
            try:
                # Extract and clean data
                title = article.get('title', '').strip()
                url = article.get('link', '')
                snippet = article.get('snippet', '').strip()
                # source = article.get('source', '')
                date_str = article.get('date', '')
                
                # Parse date
                published_date = self._parse_date(date_str)
                
                # Determine country/region
                # country_region = self._determine_country_region(title, snippet, source)
                
                # Determine language
                # language = self._determine_language(title, snippet)
                
                processed_article = {
                    'Project Title': title,
                    'Source URL': url,
                    'Summary': snippet,
                    # 'Country/Region': country_region,
                    # 'Language': language,
                    'Date Published': published_date,
                    'Week Collected': current_week
                }
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
        
        return processed_articles
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and format date string for both absolute and relative formats"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        try:
            # Handle relative date formats (Bing News)
            now = datetime.now()
            if date_str.endswith('m'):
                return now.strftime('%Y-%m-%d')
            elif date_str.endswith('h'):
                hours = int(date_str[:-1])
                parsed_date = now - timedelta(hours=hours)
                return parsed_date.strftime('%Y-%m-%d')
            elif date_str.endswith('d'):
                days = int(date_str[:-1])
                parsed_date = now - timedelta(days=days)
                return parsed_date.strftime('%Y-%m-%d')
            elif date_str.endswith('mon'):
                months = int(date_str[:-3])
                parsed_date = now - timedelta(days=months*30)
                return parsed_date.strftime('%Y-%m-%d')
            elif date_str.endswith('y'):
                years = int(date_str[:-1])
                parsed_date = now - timedelta(days=years*365)
                return parsed_date.strftime('%Y-%m-%d')
            # Handle absolute date formats (Google News)
            date_formats = [
                '%m/%d/%Y, %I:%M %p, +0000 UTC',  # 04/19/2012, 07:00 AM, +0000 UTC
                '%m/%d/%Y, %I:%M %p',  # 11/12/2024, 09:03 AM
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y'
            ]
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            # If no format matches, return current date
            return datetime.now().strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def _determine_country_region(self, title: str, snippet: str, source: str) -> str:
        """Determine country/region based on content and source"""
        content = f"{title} {snippet} {source}".lower()
        
        # Check for specific countries in the region
        countries = self.config.REGIONS[self.region]['countries']
        
        for country in countries:
            if country.lower() in content:
                return country
        
        # Return region name if no specific country found
        return self.region.upper()
    
    def _determine_language(self, title: str, snippet: str) -> str:
        """Determine language of the content"""
        content = f"{title} {snippet}".lower()
        
        # Simple language detection based on common words
        english_words = ['the', 'and', 'for', 'with', 'aircraft', 'hangar', 'maintenance']
        german_words = ['der', 'die', 'das', 'und', 'für', 'mit', 'flugzeug', 'halle']
        french_words = ['le', 'la', 'les', 'et', 'pour', 'avec', 'avion', 'hangar']
        
        if any(word in content for word in english_words):
            return 'English'
        elif any(word in content for word in german_words):
            return 'German'
        elif any(word in content for word in french_words):
            return 'French'
        else:
            return 'English'  # Default to English
    
    def _parse_article_date(self, date_str: str) -> Optional[datetime]:
        """Parse article date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Handle various date formats
            date_formats = [
                '%m/%d/%Y, %I:%M %p, +0000 UTC',  # 04/19/2012, 07:00 AM, +0000 UTC
                '%m/%d/%Y, %I:%M %p',  # 11/12/2024, 09:03 AM
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None 