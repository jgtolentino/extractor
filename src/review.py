from typing import List, Dict, Optional
import pandas as pd
import logging
from .extracters.pubmed import PubMedExtractor
from .extracters.cochrane import CochraneExtractor
from .extracters.clinicaltrials import ClinicalTrialsExtractor
from .extracters.paper_data import PaperDataExtractor
from .exporters.excel import ExcelExporter
from .exporters.csv import CSVExporter
from .exporters.stats import StatsGenerator
from .exporters.validator import DataValidator

class SystematicReview:
    def __init__(self, email: str):
        """Initialize systematic review with extractors"""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize extractors
        self.pubmed = PubMedExtractor(email)
        self.cochrane = CochraneExtractor()
        self.clinicaltrials = ClinicalTrialsExtractor()
        self.paper_extractor = PaperDataExtractor()
        
        # Initialize exporters
        self.excel_exporter = ExcelExporter()
        self.csv_exporter = CSVExporter()
        
        self.results = []
        
    def search_databases(
        self, 
        query: str, 
        max_results: int = 100,
        include_cochrane: bool = True,
        include_clinicaltrials: bool = True
    ) -> None:
        """Search across multiple databases"""
        # PubMed search
        logging.info("Searching PubMed...")
        pmids = self.pubmed.search(query, max_results)
        for pmid in pmids:
            article = self.pubmed.fetch_details(pmid)
            try:
                metadata = self.paper_extractor.extract_metadata(article)
                self.results.append({
                    'source': 'pubmed',
                    'data': metadata.__dict__
                })
            except ValueError as e:
                logging.error(f"Failed to extract metadata for PMID {pmid}: {str(e)}")
            
        # Cochrane Library search
        if include_cochrane:
            logging.info("Searching Cochrane Library...")
            cochrane_results = self.cochrane.search(query, max_results)
            for article in cochrane_results:
                try:
                    metadata = self.paper_extractor.extract_metadata(article)
                    self.results.append({
                        'source': 'cochrane',
                        'data': metadata.__dict__
                    })
                except ValueError as e:
                    logging.error(f"Failed to extract Cochrane metadata: {str(e)}")
                
        # ClinicalTrials.gov search
        if include_clinicaltrials:
            logging.info("Searching ClinicalTrials.gov...")
            ct_results = self.clinicaltrials.search(query, max_results)
            for trial in ct_results:
                try:
                    metadata = self.paper_extractor.extract_metadata(trial)
                    self.results.append({
                        'source': 'clinicaltrials',
                        'data': metadata.__dict__
                    })
                except ValueError as e:
                    logging.error(f"Failed to extract ClinicalTrials metadata: {str(e)}")
                    
    def export_results(self, format: str = 'csv', filename: str = 'systematic_review_results') -> str:
        """Export results to specified format"""
        data = [r['data'] for r in self.results]
        
        try:
            if format == 'csv':
                return self.csv_exporter.export(data, filename)
            elif format == 'excel':
                return self.excel_exporter.export(data, filename)
            else:
                raise ValueError("Supported formats: 'csv', 'excel'")
        except Exception as e:
            logging.error(f"Export failed: {str(e)}")
            raise
            
    def generate_statistics(self) -> Dict:
        """Generate statistical analysis of results"""
        try:
            stats_generator = StatsGenerator([r['data'] for r in self.results])
            return {
                'summary': stats_generator.generate_summary_stats(),
                'meta_analysis': stats_generator.generate_meta_analysis()
            }
        except Exception as e:
            logging.error(f"Statistics generation failed: {str(e)}")
            return {}
            
    def validate_data(self, generate_report: bool = True) -> Dict:
        """Validate extracted data and optionally generate report"""
        try:
            validator = DataValidator([r['data'] for r in self.results])
            validation_results = validator.validate_all()
            
            if generate_report:
                validator.generate_report('validation_report.txt')
                
            return validation_results
        except Exception as e:
            logging.error(f"Data validation failed: {str(e)}")
            return {}