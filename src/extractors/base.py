from typing import Optional, Dict
import requests
import time
import logging

class BaseExtractor:
    def __init__(self, delay: int):
        """Initialize base extractor with rate limiting delay"""
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def _make_request(self, 
                     method: str, 
                     url: str, 
                     params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make HTTP request with rate limiting and error handling"""
        try:
            time.sleep(self.delay)  # Rate limiting
            response = requests.request(
                method,
                url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self._handle_error(f"Request failed: {url}", e)
            return None
            
    def _handle_error(self, message: str, error: Exception) -> None:
        """Handle and log errors"""
        logging.error(f"{message}: {str(error)}")