from typing import Dict, Optional, List
import re
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class PaperMetadata:
    title: str
    authors: List[str]
    doi: Optional[str]
    year: Optional[int]
    sample_size: Optional[int]
    study_type: Optional[str]
    full_text_links: List[str]

class PaperDataExtractor:
    """Extract and validate research paper metadata"""
    
    DOI_PATTERN = r'10.\d{4,9}/[-._;()/:\w]+'
    STUDY_TYPES = {
        'RCT': ['randomized', 'randomised', 'rct'],
        'Cohort': ['cohort', 'longitudinal'],
        'Case-Control': ['case-control', 'case control'],
        'Meta-Analysis': ['meta-analysis', 'meta analysis'],
        'Systematic Review': ['systematic review'],
        'Observational': ['observational', 'cross-sectional']
    }

    def extract_metadata(self, paper_data: Dict) -> PaperMetadata:
        """Extract and validate paper metadata from raw data"""
        try:
            # Extract basic metadata
            title = self._validate_title(paper_data.get('TI', paper_data.get('title', '')))
            authors = self._extract_authors(paper_data)
            doi = self._extract_doi(paper_data)
            year = self._extract_year(paper_data)
            
            # Extract study details
            sample_size = self._extract_sample_size(paper_data)
            study_type = self._detect_study_type(paper_data)
            full_text_links = self._extract_full_text_links(paper_data)

            return PaperMetadata(
                title=title,
                authors=authors,
                doi=doi,
                year=year,
                sample_size=sample_size,
                study_type=study_type,
                full_text_links=full_text_links
            )

        except Exception as e:
            logging.error(f"Error extracting metadata: {str(e)}")
            raise ValueError(f"Failed to extract paper metadata: {str(e)}")

    def _validate_title(self, title: str) -> str:
        """Validate and clean paper title"""
        if not title or len(title.strip()) < 3:
            raise ValueError("Invalid or missing title")
        return title.strip()

    def _extract_authors(self, data: Dict) -> List[str]:
        """Extract and validate author list"""
        authors = []
        
        # Handle different author field formats
        raw_authors = data.get('AU', data.get('authors', data.get('FAU', [])))
        
        if isinstance(raw_authors, str):
            raw_authors = [a.strip() for a in raw_authors.split(',')]
            
        for author in raw_authors:
            author = author.strip()
            if author and len(author) > 1:
                authors.append(author)
                
        if not authors:
            logging.warning("No valid authors found")
            
        return authors

    def _extract_doi(self, data: Dict) -> Optional[str]:
        """Extract and validate DOI"""
        doi = data.get('DOI', data.get('doi', ''))
        
        if doi:
            doi_match = re.search(self.DOI_PATTERN, doi)
            if doi_match:
                return doi_match.group(0)
                
        return None

    def _extract_year(self, data: Dict) -> Optional[int]:
        """Extract and validate publication year"""
        try:
            # Try different date fields
            for field in ['DP', 'PDAT', 'publication_date', 'year']:
                date_str = data.get(field)
                if date_str:
                    # Try different date formats
                    for fmt in ['%Y', '%Y/%m/%d', '%Y-%m-%d', '%Y %b %d']:
                        try:
                            return datetime.strptime(date_str.split()[0], fmt).year
                        except ValueError:
                            continue
                            
            return None
            
        except Exception as e:
            logging.warning(f"Failed to extract year: {str(e)}")
            return None

    def _extract_sample_size(self, data: Dict) -> Optional[int]:
        """Extract sample size from paper data"""
        try:
            # Look for sample size in abstract or methods
            text = ' '.join([
                data.get('AB', ''),
                data.get('abstract', ''),
                data.get('methods', '')
            ]).lower()
            
            # Common patterns for sample size reporting
            patterns = [
                r'n\s*=\s*(\d+)',
                r'sample size (?:of|was|=)\s*(\d+)',
                r'enrolled\s*(\d+)\s*participants',
                r'included\s*(\d+)\s*patients'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return int(match.group(1))
                    
            return None
            
        except Exception as e:
            logging.warning(f"Failed to extract sample size: {str(e)}")
            return None

    def _detect_study_type(self, data: Dict) -> Optional[str]:
        """Detect study type from paper data"""
        try:
            # Combine relevant fields for analysis
            text = ' '.join([
                data.get('TI', ''),
                data.get('AB', ''),
                data.get('PT', ''),
                data.get('publication_type', ''),
            ]).lower()
            
            # Check for each study type
            for study_type, keywords in self.STUDY_TYPES.items():
                if any(keyword in text for keyword in keywords):
                    return study_type
                    
            return None
            
        except Exception as e:
            logging.warning(f"Failed to detect study type: {str(e)}")
            return None

    def _extract_full_text_links(self, data: Dict) -> List[str]:
        """Extract full text links from paper data"""
        links = []
        
        try:
            # Check various fields for URLs
            for field in ['LID', 'OUR', 'full_text_url']:
                urls = data.get(field, [])
                if isinstance(urls, str):
                    urls = [urls]
                    
                for url in urls:
                    if url.startswith(('http://', 'https://')):
                        links.append(url)
                        
            # Add DOI-based link if available
            doi = self._extract_doi(data)
            if doi:
                links.append(f"https://doi.org/{doi}")
                
        except Exception as e:
            logging.warning(f"Failed to extract full text links: {str(e)}")
            
        return list(set(links))  # Remove duplicates