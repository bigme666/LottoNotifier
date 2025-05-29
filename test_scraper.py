#!/usr/bin/env python3
"""
Test script for the lottery scraper without Telegram dependencies.
This allows us to test the scraping functionality independently.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_lotto_scraping():
    """Test the lottery scraping functionality."""
    url = "https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g"
    
    print(f"Testing scraping from: {url}")
    
    try:
        # Test basic HTTP request
        response = requests.get(url, timeout=30)
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for lottery-related content
            print("\nSearching for lottery data...")
            
            # Check for tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            # Check for content with lottery keywords
            lotto_content = soup.find_all(text=lambda text: text and any(
                keyword in text.lower() for keyword in ['lotto', 'estrazione', 'ruota', 'numero']
            ))
            
            print(f"Found {len(lotto_content)} text elements with lottery keywords")
            
            # Look for specific lottery cities
            cities = ['Bari', 'Cagliari', 'Firenze', 'Genova', 'Milano', 'Napoli', 'Palermo', 'Roma', 'Torino', 'Venezia']
            found_cities = []
            
            for city in cities:
                if city.lower() in response.text.lower():
                    found_cities.append(city)
            
            print(f"Found cities: {', '.join(found_cities)}")
            
            # Check if page contains dynamic content indicators
            scripts = soup.find_all('script')
            has_js = len([s for s in scripts if s.string and 'javascript' in str(s).lower()]) > 0
            
            print(f"Page has {len(scripts)} script tags (dynamic content: {has_js})")
            
            # Return basic analysis
            return {
                'status': 'success',
                'tables_found': len(tables),
                'cities_found': found_cities,
                'has_dynamic_content': has_js,
                'content_length': len(response.text)
            }
            
        else:
            return {
                'status': 'failed',
                'error': f'HTTP {response.status_code}',
                'content_length': len(response.text) if response.text else 0
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    print("=== Lottery Scraper Test ===")
    result = test_lotto_scraping()
    print(f"\nResult:")
    print(json.dumps(result, indent=2, ensure_ascii=False))