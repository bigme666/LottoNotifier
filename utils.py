import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def format_lottery_results(results: Dict) -> str:
    """
    Format lottery results into a readable message for Telegram.
    
    Args:
        results: Dictionary containing lottery data
        
    Returns:
        Formatted string message
    """
    if not results:
        return "Nessun risultato disponibile al momento."
    
    message_lines = []
    
    # Header
    message_lines.append("LOTTO - Risultati Ultima Estrazione")
    message_lines.append("")
    
    # Add extraction info if available
    if 'extraction_date' in results:
        message_lines.append(f"Data: {results['extraction_date']}")
    if 'extraction_number' in results and results['extraction_number']:
        message_lines.append(f"Estrazione N: {results['extraction_number']}")
    
    if 'extraction_date' in results:
        message_lines.append("")
    
    # Add results for each city in compact format
    if 'cities' in results:
        for city, numbers in results['cities'].items():
            if numbers:
                numbers_str = " ".join(f"{num:>2}" for num in numbers)
                message_lines.append(f"{city:<10}: {numbers_str}")
    
    # Footer
    message_lines.append("")
    message_lines.append(f"Fonte: {results.get('source', 'RAI Televideo')}")
    if 'timestamp' in results:
        message_lines.append(f"Aggiornato: {results['timestamp']}")
    
    return "\n".join(message_lines)

def validate_lottery_data(data: Dict) -> bool:
    """
    Validate that lottery data contains expected structure.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Check for required fields
    required_fields = ['cities']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Check that cities data is properly structured
    cities = data.get('cities', {})
    if not isinstance(cities, dict):
        return False
    
    # Validate that each city has numeric data
    for city, numbers in cities.items():
        if numbers and not all(isinstance(num, (int, str)) for num in numbers):
            logger.warning(f"Invalid number format for city {city}")
            return False
    
    return True

def rate_limit_delay(last_request_time: Optional[float], min_interval: float = 1.0) -> None:
    """
    Implement rate limiting by adding delay if needed.
    
    Args:
        last_request_time: Timestamp of last request
        min_interval: Minimum interval between requests in seconds
    """
    if last_request_time:
        elapsed = time.time() - last_request_time
        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

def get_current_timestamp() -> str:
    """
    Get current timestamp in Italian format.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
