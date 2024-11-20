import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from .base import BaseExtractor

class ClinicalTrialsExtractor(BaseExtractor):
    def __init__(self, delay: int = 2):
        """Initialize ClinicalTrials.gov extractor"""
        super().__init__(delay)
        self.base_url = "https://clinicaltrials.gov/api"
        
    def search(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search ClinicalTrials.gov and return list of trials
        Includes rate limiting and error handling
        """
        try:
            params = {
                'expr': query,
                'fmt': 'json',  # API supports JSON format
                'max_rnk': max_results
            }
            
            response = self._make_request('GET', 
                                        f"{self.base_url}/query/study_fields", 
                                        params=params)
            
            if not response:
                return []
            
            data = response.json()
            results = []
            
            for study in data.get('StudyFieldsResponse', {}).get('StudyFields', []):
                results.append({
                    'nct_id': self._get_first(study.get('NCTId')),
                    'title': self._get_first(study.get('BriefTitle')),
                    'status': self._get_first(study.get('OverallStatus')),
                    'conditions': study.get('Condition', []),
                    'interventions': study.get('InterventionName', []),
                    'source': 'clinicaltrials'
                })
                
            return results
            
        except Exception as e:
            self._handle_error("ClinicalTrials.gov search failed", e)
            return []
            
    def _get_first(self, list_value: List) -> str:
        """Helper to get first item from list or empty string"""
        return list_value[0] if list_value else ''