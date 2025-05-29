import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional
import logging
from config import LOTTO_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, USER_AGENT
from utils import rate_limit_delay, validate_lottery_data

logger = logging.getLogger(__name__)

class LottoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.last_request_time = None
    
    def fetch_page(self) -> Optional[str]:
        """
        Fetch the lottery results page with retry logic.
        
        Returns:
            HTML content of the page or None if failed
        """
        for attempt in range(MAX_RETRIES):
            try:
                # Implement rate limiting
                rate_limit_delay(self.last_request_time, 2.0)
                
                logger.info(f"Fetching lottery data (attempt {attempt + 1}/{MAX_RETRIES})")
                response = self.session.get(LOTTO_URL, timeout=REQUEST_TIMEOUT)
                self.last_request_time = time.time()
                
                response.raise_for_status()
                
                if response.status_code == 200:
                    logger.info("Successfully fetched lottery page")
                    return response.text
                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("Max retries exceeded")
        
        return None
    
    def parse_lottery_results(self, html_content: str) -> Dict:
        """
        Parse lottery results from HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Dictionary containing parsed lottery data
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = {
                'cities': {},
                'date': None,
                'extraction_number': None
            }
            
            # Look for the main content area
            # The structure may vary, so we'll try multiple selectors
            content_selectors = [
                '.content-lottery',
                '.lotto-results',
                '.estrazione',
                'table',
                '.table'
            ]
            
            content_area = None
            for selector in content_selectors:
                content_area = soup.select_one(selector)
                if content_area:
                    logger.info(f"Found content area with selector: {selector}")
                    break
            
            if not content_area:
                # If no specific content area found, use the whole body
                content_area = soup.find('body') or soup
                logger.info("Using entire page body for parsing")
            
            # Extract date information
            date_patterns = [
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4})'
            ]
            
            page_text = content_area.get_text()
            for pattern in date_patterns:
                date_match = re.search(pattern, page_text)
                if date_match:
                    results['date'] = date_match.group(1)
                    logger.info(f"Found extraction date: {results['date']}")
                    break
            
            # Extract extraction number
            extraction_patterns = [
                r'(?:concorso|estrazione|n\.?)\s*(\d+)',
                r'(\d+)°\s*(?:concorso|estrazione)',
            ]
            
            for pattern in extraction_patterns:
                extraction_match = re.search(pattern, page_text, re.IGNORECASE)
                if extraction_match:
                    results['extraction_number'] = extraction_match.group(1)
                    logger.info(f"Found extraction number: {results['extraction_number']}")
                    break
            
            # Common Italian city names for lottery
            italian_cities = [
                'BARI', 'CAGLIARI', 'FIRENZE', 'GENOVA', 'MILANO', 
                'NAPOLI', 'PALERMO', 'ROMA', 'TORINO', 'VENEZIA', 'NAZIONALE'
            ]
            
            # Try to find tables with lottery data
            tables = content_area.find_all('table')
            
            if tables:
                logger.info(f"Found {len(tables)} tables")
                for table in tables:
                    self._parse_table_results(table, results, italian_cities)
            else:
                # If no tables, try to parse from text content
                logger.info("No tables found, trying text parsing")
                self._parse_text_results(content_area, results, italian_cities)
            
            # Validate and clean results
            if results['cities']:
                logger.info(f"Successfully parsed results for {len(results['cities'])} cities")
                return results
            else:
                logger.warning("No lottery results found in parsed content")
                return {}
                
        except Exception as e:
            logger.error(f"Error parsing lottery results: {e}")
            return {}
    
    def _parse_table_results(self, table, results: Dict, cities: List[str]) -> None:
        """
        Parse lottery results from table elements.
        
        Args:
            table: BeautifulSoup table element
            results: Results dictionary to update
            cities: List of city names to look for
        """
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Check if first cell contains a city name
                first_cell_text = cells[0].get_text(strip=True).upper()
                
                for city in cities:
                    if city in first_cell_text:
                        # Extract numbers from subsequent cells
                        numbers = []
                        for cell in cells[1:]:
                            cell_text = cell.get_text(strip=True)
                            # Look for numbers in the cell
                            found_numbers = re.findall(r'\b\d{1,2}\b', cell_text)
                            numbers.extend(found_numbers)
                        
                        if numbers:
                            results['cities'][city] = numbers[:5]  # Limit to 5 numbers
                            logger.info(f"Found numbers for {city}: {numbers[:5]}")
                        break
    
    def _parse_text_results(self, content_area, results: Dict, cities: List[str]) -> None:
        """
        Parse lottery results from text content when no tables are found.
        
        Args:
            content_area: BeautifulSoup element containing content
            results: Results dictionary to update
            cities: List of city names to look for
        """
        text_content = content_area.get_text()
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip().upper()
            if not line:
                continue
            
            for city in cities:
                if city in line:
                    # Extract numbers from the line
                    numbers = re.findall(r'\b\d{1,2}\b', line)
                    if len(numbers) >= 5:  # Ensure we have enough numbers
                        results['cities'][city] = numbers[:5]
                        logger.info(f"Found numbers for {city}: {numbers[:5]}")
                    break
    
    def get_latest_results(self) -> Dict:
        """
        Get the latest lottery results.
        
        Returns:
            Dictionary containing lottery results or empty dict if failed
        """
        logger.info("Starting lottery results scraping")
        
        html_content = self.fetch_page()
        if not html_content:
            logger.error("Failed to fetch lottery page")
            return {}
        
        results = self.parse_lottery_results(html_content)
        
        if validate_lottery_data(results):
            logger.info("Successfully scraped and validated lottery results")
            return results
        else:
            logger.error("Scraped data failed validation")
            return {}
