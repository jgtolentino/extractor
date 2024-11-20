import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .base import BaseExtractor

class CochraneExtractor(BaseExtractor):
    def __init__(self, delay: int = 3):
        """Initialize Cochrane Library extractor"""
        super().__init__(delay)
        self.base_url = "https://www.cochranelibrary.com"
        self.search_url = f"{self.base_url}/advanced-search"
        
    def search(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search Cochrane Library and return list of reviews
        Includes rate limiting and error handling
        """
        try:
            params = {
                'searchText': query,
                'fromYear': '',
                'toYear': '',
                'selectedReviewGroups': '',
            }
            
            response = self._make_request('GET', 
                                        self.search_url, 
                                        params=params)
            
            if not response:
                return []
                
            soup = BeautifulSoup(response.text, 'lxml')
            results = []
            
            # Parse search results
            articles = soup.find_all('article', class_='search-result')
            for article in articles[:max_results]:
                title = article.find('h3').text.strip()
                authors = article.find('div', class_='search-result-authors')
                authors = authors.text.strip() if authors else ''
                
                results.append({
                    'title': title,
                    'authors': authors,
                    'source': 'cochrane',
                    'url': self.base_url + article.find('a')['href']
                })
                
            return results
            
        except Exception as e:
            self._handle_error("Cochrane Library search failed", e)
            return []