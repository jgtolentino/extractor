from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import pandas as pd
import logging
from pathlib import Path

class BaseExporter(ABC):
    """Base class for data exporters"""
    
    def __init__(self, output_dir: str = 'exports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _prepare_data(self, data: List[Dict]) -> pd.DataFrame:
        """Convert data to DataFrame with validation"""
        try:
            df = pd.DataFrame(data)
            return self._clean_dataframe(df)
        except Exception as e:
            logging.error(f"Data preparation failed: {str(e)}")
            raise ValueError("Failed to prepare data for export")
            
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize DataFrame"""
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Convert date columns to datetime
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        return df
        
    @abstractmethod
    def export(self, data: List[Dict], filename: str) -> str:
        """Export data to file"""
        pass