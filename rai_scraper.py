import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional
import logging
from config import LOTTO_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, USER_AGENT
from utils import rate_limit_delay, validate_lottery_data

logger = logging.getLogger(__name__)

class RaiLottoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.last_request_time = None

    def fetch_page(self) -> Optional[str]:
        """
        Fetch the lottery results page from RAI Televideo.
        
        Returns:
            HTML content of the page or None if failed
        """
        for attempt in range(MAX_RETRIES):
            try:
                rate_limit_delay(self.last_request_time, 2.0)
                
                logger.info(f"Fetching lottery data from RAI Televideo (attempt {attempt + 1}/{MAX_RETRIES})")
                logger.info(f"URL: {LOTTO_URL}")
                
                response = self.session.get(LOTTO_URL, timeout=REQUEST_TIMEOUT)
                self.last_request_time = time.time()
                
                response.raise_for_status()
                
                if response.status_code == 200:
                    logger.info("Successfully fetched lottery page from RAI Televideo")
                    return response.text
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("All request attempts failed")
        
        return None

    def parse_lottery_results(self, html_content: str) -> Dict:
        """
        Parse lottery results from RAI Televideo HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Dictionary containing parsed lottery data
        """
        logger.info("Parsing lottery results from RAI Televideo")
        
        results = {
            'source': 'RAI Televideo',
            'url': LOTTO_URL,
            'cities': {},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'extraction_date': None,
            'extraction_number': None
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for the main content in RAI Televideo format
            # RAI Televideo typically uses pre tags or specific div structures
            content_areas = soup.find_all(['pre', 'div', 'p', 'span'])
            
            # Italian city names to look for
            cities = [
                'BARI', 'CAGLIARI', 'FIRENZE', 'GENOVA', 'MILANO', 
                'NAPOLI', 'PALERMO', 'ROMA', 'TORINO', 'VENEZIA', 'NAZIONALE'
            ]
            
            # Process all content areas
            for content_area in content_areas:
                if content_area and content_area.get_text():
                    text_content = content_area.get_text()
                    self._parse_text_results(text_content, results, cities)
            
            # Also try to extract extraction date and number
            self._extract_extraction_info(soup, results)
            
            logger.info(f"Parsed results for {len(results['cities'])} cities")
            
        except Exception as e:
            logger.error(f"Error parsing lottery results: {e}")
        
        return results

    def _parse_text_results(self, text_content: str, results: Dict, cities: List[str]) -> None:
        """
        Parse lottery results from text content.
        
        Args:
            text_content: Text content to parse
            results: Results dictionary to update
            cities: List of city names to look for
        """
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip().upper()
            if not line:
                continue
                
            # Look for city names in the line
            for city in cities:
                if city in line:
                    # Extract numbers from the line (looking for sequences of 1-2 digit numbers)
                    numbers = re.findall(r'\b\d{1,2}\b', line)
                    
                    # Filter out very large numbers that are likely not lottery numbers
                    lottery_numbers = [num for num in numbers if 1 <= int(num) <= 90]
                    
                    if len(lottery_numbers) >= 5:  # Ensure we have enough numbers
                        results['cities'][city] = lottery_numbers[:5]
                        logger.info(f"Found numbers for {city}: {lottery_numbers[:5]}")
                    elif len(lottery_numbers) >= 3:  # Accept partial results
                        results['cities'][city] = lottery_numbers
                        logger.info(f"Found partial numbers for {city}: {lottery_numbers}")
                    break

    def _extract_extraction_info(self, soup: BeautifulSoup, results: Dict) -> None:
        """
        Extract extraction date and number information.
        
        Args:
            soup: BeautifulSoup object
            results: Results dictionary to update
        """
        try:
            # Look for date and extraction number patterns
            text_content = soup.get_text()
            
            # Look for date patterns (various Italian formats)
            date_patterns = [
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',  # DD/MM/YYYY, DD-MM-YYYY, etc.
                r'(\d{1,2}\s+[A-Za-z]+\s+\d{2,4})',  # DD Month YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text_content)
                if match:
                    results['extraction_date'] = match.group(1)
                    break
            
            # Look for extraction number patterns
            extraction_patterns = [
                r'ESTRAZIONE\s+N[°.]?\s*(\d+)',
                r'N[°.]?\s*(\d+)',
                r'CONCORSO\s+(\d+)',
            ]
            
            for pattern in extraction_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    results['extraction_number'] = match.group(1)
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting extraction info: {e}")

    def get_latest_results(self) -> Dict:
        """
        Get the latest lottery results from RAI Televideo.
        
        Returns:
            Dictionary containing lottery results or empty dict if failed
        """
        logger.info("Starting lottery results scraping from RAI Televideo")
        
        html_content = self.fetch_page()
        if not html_content:
            logger.error("Failed to fetch lottery page")
            return {}
        
        results = self.parse_lottery_results(html_content)
        
        if validate_lottery_data(results):
            logger.info("Successfully scraped and validated lottery results")
            return results
        else:
            logger.warning("Scraped results failed validation")
            return results  # Return anyway, let the caller decide what to do