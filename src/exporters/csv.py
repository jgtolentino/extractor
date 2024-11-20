from typing import List, Dict
import pandas as pd
from .base import BaseExporter
import logging

class CSVExporter(BaseExporter):
    """Export data to CSV with encoding handling"""
    
    def export(self, data: List[Dict], filename: str) -> str:
        """Export data to CSV file"""
        try:
            df = self._prepare_data(data)
            output_path = self.output_dir / f"{filename}.csv"
            
            # Export with UTF-8 encoding and BOM for Excel compatibility
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            return str(output_path)
            
        except Exception as e:
            logging.error(f"CSV export failed: {str(e)}")
            raise