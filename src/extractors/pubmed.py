from Bio import Entrez
import pandas as pd
from typing import List, Dict, Optional
import time
from .base import BaseExtractor

class PubMedExtractor(BaseExtractor):
    def __init__(self, email: str, delay: int = 1):
        """Initialize PubMed extractor with user email (required by NCBI)"""
        super().__init__(delay)
        Entrez.email = email
        
    def search(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search PubMed and return list of PMIDs
        Includes rate limiting and error handling
        """
        try:
            time.sleep(self.delay)  # Rate limiting
            handle = Entrez.esearch(db="pubmed", 
                                  term=query, 
                                  retmax=max_results,
                                  usehistory="y")
            results = Entrez.read(handle)
            handle.close()
            return results["IdList"]
        except Exception as e:
            self._handle_error("PubMed search failed", e)
            return []
    
    def fetch_details(self, pmid: str) -> Dict:
        """Fetch detailed information for a single PMID"""
        try:
            time.sleep(self.delay)  # Rate limiting
            handle = Entrez.efetch(db="pubmed", 
                                 id=pmid, 
                                 rettype="medline", 
                                 retmode="text")
            record = handle.read()
            handle.close()
            return self._parse_medline(record)
        except Exception as e:
            self._handle_error(f"Failed to fetch details for PMID {pmid}", e)
            return {}
    
    def _parse_medline(self, record: str) -> Dict:
        """Parse MEDLINE format record into structured data"""
        data = {}
        current_field = None
        
        for line in record.split('\n'):
            if not line.strip():
                continue
            if line.startswith('      '):  # Continuation of previous field
                if current_field:
                    data[current_field] += ' ' + line.strip()
            elif line.startswith('PMID'):
                data['pmid'] = line.split('-', 1)[1].strip()
            else:
                try:
                    field, value = line.split('-', 1)
                    current_field = field.strip()
                    data[current_field] = value.strip()
                except ValueError:
                    continue
                    
        return data