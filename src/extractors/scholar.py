import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time

class ScholarExtractor:
    def __init__(self, delay: int = 3):
        """Initialize Google Scholar extractor with delay between requests"""
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search Google Scholar and return list of articles"""
        results = []
        
        try:
            response = requests.get(
                f"https://scholar.google.com/scholar?q={query}&hl=en",
                headers=self.headers
            )
            soup = BeautifulSoup(response.text, 'lxml')
            
            articles = soup.find_all('div', class_='gs_ri')
            for article in articles[:max_results]:
                title = article.find('h3', class_='gs_rt').text
                snippet = article.find('div', class_='gs_rs').text
                authors = article.find('div', class_='gs_a').text
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'authors': authors
                })
                
            time.sleep(self.delay)  # Respect rate limits
            
        except Exception as e:
            print(f"Error during Scholar extraction: {str(e)}")
            
        return results