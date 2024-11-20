from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    completeness_score: float
    consistency_score: float
    validity_score: float
    overall_score: float
    issues: List[str]

class QualityChecker:
    """Check data quality and completeness"""
    
    def __init__(self, required_fields: Optional[List[str]] = None):
        self.required_fields = required_fields or [
            'title', 'authors', 'year', 'doi', 'sample_size'
        ]
        self.logger = logging.getLogger(__name__)
        
    def check_quality(self, data: List[Dict]) -> QualityMetrics:
        """Perform comprehensive quality check"""
        try:
            df = pd.DataFrame(data)
            
            completeness = self._check_completeness(df)
            consistency = self._check_consistency(df)
            validity = self._check_validity(df)
            
            issues = []
            issues.extend(self._get_completeness_issues(completeness))
            issues.extend(self._get_consistency_issues(consistency))
            issues.extend(self._get_validity_issues(validity))
            
            overall_score = (
                completeness['score'] * 0.4 +
                consistency['score'] * 0.3 +
                validity['score'] * 0.3
            )
            
            return QualityMetrics(
                completeness_score=completeness['score'],
                consistency_score=consistency['score'],
                validity_score=validity['score'],
                overall_score=overall_score,
                issues=issues
            )
            
        except Exception as e:
            self.logger.error(f"Quality check failed: {str(e)}")
            raise
            
    def _check_completeness(self, df: pd.DataFrame) -> Dict:
        """Check data completeness"""
        field_scores = {}
        for field in self.required_fields:
            if field in df.columns:
                completeness = (df[field].notna().mean() * 100)
                field_scores[field] = completeness
            else:
                field_scores[field] = 0
                
        return {
            'scores': field_scores,
            'score': sum(field_scores.values()) / len(field_scores)
        }
        
    def _check_consistency(self, df: pd.DataFrame) -> Dict:
        """Check data consistency"""
        checks = {
            'year_format': self._check_year_format(df),
            'author_format': self._check_author_format(df),
            'doi_format': self._check_doi_format(df)
        }
        
        score = sum(1 for check in checks.values() if check) / len(checks) * 100
        
        return {
            'checks': checks,
            'score': score
        }
        
    def _check_validity(self, df: pd.DataFrame) -> Dict:
        """Check data validity"""
        current_year = datetime.now().year
        issues = []
        
        if 'year' in df.columns:
            invalid_years = df[
                (df['year'] < 1800) | 
                (df['year'] > current_year)
            ]
            if not invalid_years.empty:
                issues.append(f"Found {len(invalid_years)} invalid publication years")
                
        if 'sample_size' in df.columns:
            invalid_samples = df[df['sample_size'] <= 0]
            if not invalid_samples.empty:
                issues.append(f"Found {len(invalid_samples)} invalid sample sizes")
                
        score = max(0, 100 - (len(issues) * 10))
        
        return {
            'issues': issues,
            'score': score
        }
        
    def _get_completeness_issues(self, completeness: Dict) -> List[str]:
        """Get completeness-related issues"""
        issues = []
        for field, score in completeness['scores'].items():
            if score < 90:
                issues.append(f"Low completeness for {field}: {score:.1f}%")
        return issues
        
    def _get_consistency_issues(self, consistency: Dict) -> List[str]:
        """Get consistency-related issues"""
        issues = []
        for check, passed in consistency['checks'].items():
            if not passed:
                issues.append(f"Failed consistency check: {check}")
        return issues
        
    def _get_validity_issues(self, validity: Dict) -> List[str]:
        """Get validity-related issues"""
        return validity['issues']
        
    def _check_year_format(self, df: pd.DataFrame) -> bool:
        """Check year format consistency"""
        if 'year' not in df.columns:
            return True
        return df['year'].dtype in [pd.Int64Dtype(), pd.Float64Dtype()]
        
    def _check_author_format(self, df: pd.DataFrame) -> bool:
        """Check author format consistency"""
        if 'authors' not in df.columns:
            return True
        return all(isinstance(authors, list) for authors in df['authors'])
        
    def _check_doi_format(self, df: pd.DataFrame) -> bool:
        """Check DOI format consistency"""
        if 'doi' not in df.columns:
            return True
        doi_pattern = r'10.\d{4,9}/[-._;()/:\w]+'
        return df['doi'].str.match(doi_pattern, na=True).all()