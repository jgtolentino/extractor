from typing import List, Dict, Optional
import pandas as pd
from .base import BaseExporter
import logging

class ExcelExporter(BaseExporter):
    """Export data to Excel with formatting"""
    
    def export(self, data: List[Dict], filename: str) -> str:
        """Export data to formatted Excel file"""
        try:
            df = self._prepare_data(data)
            output_path = self.output_dir / f"{filename}.xlsx"
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write main data
                df.to_excel(writer, sheet_name='Data', index=False)
                self._format_excel(writer, df)
                
                # Add summary sheet
                summary = self._create_summary(df)
                summary.to_excel(writer, sheet_name='Summary', index=True)
                
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Excel export failed: {str(e)}")
            raise
            
    def _format_excel(self, writer: pd.ExcelWriter, df: pd.DataFrame) -> None:
        """Apply Excel formatting"""
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        # Format headers
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, max(len(value) + 2, 12))
            
    def _create_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics DataFrame"""
        summary_data = {
            'Total Records': len(df),
            'Unique Authors': df['authors'].nunique(),
            'Publication Years': f"{df['year'].min()}-{df['year'].max()}",
            'Study Types': df['study_type'].value_counts().to_dict()
        }
        return pd.DataFrame.from_dict(summary_data, orient='index', columns=['Value'])