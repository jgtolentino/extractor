from typing import Any, Dict, List, Optional
import re
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class InputValidator:
    """Validate input data for systematic review operations"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.doi_pattern = re.compile(r'^10.\d{4,9}/[-._;()/:\w]+$')
        
    def validate_search_params(self, query: str, max_results: int) -> ValidationResult:
        """Validate search parameters"""
        errors = []
        warnings = []
        
        # Validate query
        if not query or len(query.strip()) < 3:
            errors.append("Query must be at least 3 characters long")
        elif len(query) > 1000:
            errors.append("Query exceeds maximum length of 1000 characters")
            
        # Validate max_results
        if max_results < 1:
            errors.append("max_results must be positive")
        elif max_results > 10000:
            warnings.append("Large result set may impact performance")
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email format"""
        errors = []
        warnings = []
        
        if not email:
            errors.append("Email is required")
        elif not self.email_pattern.match(email):
            errors.append("Invalid email format")
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    def validate_date_range(self, start_year: Optional[int], end_year: Optional[int]) -> ValidationResult:
        """Validate publication date range"""
        errors = []
        warnings = []
        current_year = datetime.now().year
        
        if start_year and end_year:
            if start_year > end_year:
                errors.append("Start year must be before end year")
            if start_year < 1800:
                errors.append("Start year must be after 1800")
            if end_year > current_year:
                errors.append(f"End year cannot be after {current_year}")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    def validate_doi(self, doi: str) -> ValidationResult:
        """Validate DOI format"""
        errors = []
        warnings = []
        
        if doi and not self.doi_pattern.match(doi):
            errors.append("Invalid DOI format")
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )