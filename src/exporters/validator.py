from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import logging

class DataValidator:
    """Validate and report on data quality"""
    
    def __init__(self, data: List[Dict]):
        self.df = pd.DataFrame(data)
        self.validation_results = []
        
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        try:
            return {
                'completeness': self._check_completeness(),
                'consistency': self._check_consistency(),
                'validity': self._check_validity(),
                'summary': self._generate_validation_summary()
            }
        except Exception as e:
            logging.error(f"Validation failed: {str(e)}")
            return {}
            
    def generate_report(self, output_path: str) -> None:
        """Generate validation report"""
        try:
            results = self.validate_all()
            
            with open(output_path, 'w') as f:
                f.write("Data Validation Report\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                
                # Write completeness results
                f.write("Data Completeness:\n")
                for field, score in results['completeness'].items():
                    f.write(f"- {field}: {score:.1f}%\n")
                    
                # Write consistency results
                f.write("\nData Consistency:\n")
                for check, result in results['consistency'].items():
                    f.write(f"- {check}: {'Pass' if result else 'Fail'}\n")
                    
                # Write validity results
                f.write("\nData Validity:\n")
                for field, issues in results['validity'].items():
                    f.write(f"- {field}: {len(issues)} issues found\n")
                    
                # Write summary
                f.write("\nSummary:\n")
                f.write(f"Overall Quality Score: {results['summary']['quality_score']:.1f}%\n")
                f.write(f"Total Issues Found: {results['summary']['total_issues']}\n")
                
        except Exception as e:
            logging.error(f"Report generation failed: {str(e)}")
            raise
            
    def _check_completeness(self) -> Dict:
        """Check completeness of required fields"""
        required_fields = {
            'title': 100,
            'authors': 100,
            'year': 90,
            'study_type': 80,
            'sample_size': 70
        }
        
        completeness = {}
        for field, threshold in required_fields.items():
            if field in self.df.columns:
                completeness[field] = (self.df[field].notna().mean() * 100)
                if completeness[field] < threshold:
                    self.validation_results.append(
                        f"Completeness warning: {field} ({completeness[field]:.1f}% < {threshold}%)"
                    )
                    
        return completeness
        
    def _check_consistency(self) -> Dict:
        """Check data consistency"""
        checks = {
            'valid_years': self._check_year_consistency(),
            'author_format': self._check_author_format(),
            'doi_format': self._check_doi_format()
        }
        return checks
        
    def _check_validity(self) -> Dict:
        """Check validity of data values"""
        validity_issues = {}
        
        # Check year validity
        if 'year' in self.df.columns:
            invalid_years = self.df[
                (self.df['year'] < 1900) | 
                (self.df['year'] > datetime.now().year)
            ]
            validity_issues['year'] = invalid_years.index.tolist()
            
        # Check sample size validity
        if 'sample_size' in self.df.columns:
            invalid_samples = self.df[self.df['sample_size'] <= 0]
            validity_issues['sample_size'] = invalid_samples.index.tolist()
            
        return validity_issues
        
    def _generate_validation_summary(self) -> Dict:
        """Generate overall validation summary"""
        return {
            'quality_score': self._calculate_quality_score(),
            'total_issues': len(self.validation_results),
            'validation_date': datetime.now().isoformat()
        }
        
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score"""
        weights = {
            'completeness': 0.4,
            'consistency': 0.3,
            'validity': 0.3
        }
        
        scores = {
            'completeness': self._completeness_score(),
            'consistency': self._consistency_score(),
            'validity': self._validity_score()
        }
        
        return sum(score * weights[metric] for metric, score in scores.items())
        
    def _completeness_score(self) -> float:
        """Calculate completeness score"""
        completeness = self._check_completeness()
        return sum(completeness.values()) / len(completeness)
        
    def _consistency_score(self) -> float:
        """Calculate consistency score"""
        consistency = self._check_consistency()
        return sum(1 for check in consistency.values() if check) / len(consistency) * 100
        
    def _validity_score(self) -> float:
        """Calculate validity score"""
        validity = self._check_validity()
        total_issues = sum(len(issues) for issues in validity.values())
        return max(0, 100 - (total_issues / len(self.df) * 100))
        
    def _check_year_consistency(self) -> bool:
        """Check year format consistency"""
        if 'year' not in self.df.columns:
            return True
        return self.df['year'].dtype in [np.int64, np.float64]
        
    def _check_author_format(self) -> bool:
        """Check author format consistency"""
        if 'authors' not in self.df.columns:
            return True
        return all(isinstance(authors, list) for authors in self.df['authors'])
        
    def _check_doi_format(self) -> bool:
        """Check DOI format consistency"""
        if 'doi' not in self.df.columns:
            return True
        doi_pattern = r'10.\d{4,9}/[-._;()/:\w]+'
        valid_dois = self.df['doi'].str.match(doi_pattern, na=True)
        return valid_dois.all()