from typing import Dict, Optional
import logging
import traceback
from datetime import datetime
import json
from pathlib import Path

class ErrorLogger:
    """Advanced error logging and tracking"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup error logger
        self.logger = logging.getLogger('error_logger')
        self.logger.setLevel(logging.ERROR)
        
        # File handler for all errors
        error_handler = logging.FileHandler(self.log_dir / 'errors.log')
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(error_handler)
        
        # File handler for critical errors
        critical_handler = logging.FileHandler(self.log_dir / 'critical.log')
        critical_handler.setLevel(logging.CRITICAL)
        critical_handler.setFormatter(
            logging.Formatter('%(asctime)s - CRITICAL - %(message)s')
        )
        self.logger.addHandler(critical_handler)
        
    def log_error(self, 
                  error: Exception, 
                  context: Dict = None, 
                  level: str = 'ERROR') -> None:
        """Log error with context"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        # Log to appropriate level
        if level == 'CRITICAL':
            self.logger.critical(json.dumps(error_data))
        else:
            self.logger.error(json.dumps(error_data))
            
        # Save detailed error report for investigation
        self._save_error_report(error_data)
        
    def _save_error_report(self, error_data: Dict) -> None:
        """Save detailed error report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.log_dir / f'error_report_{timestamp}.json'
        
        try:
            with open(report_path, 'w') as f:
                json.dump(error_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save error report: {str(e)}")
            
    def get_error_summary(self, days: int = 7) -> Dict:
        """Get summary of recent errors"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            error_counts = {'CRITICAL': 0, 'ERROR': 0}
            error_types = {}
            
            # Process error logs
            error_files = list(self.log_dir.glob('error_report_*.json'))
            for file_path in error_files:
                if file_path.stat().st_mtime >= cutoff_date:
                    with open(file_path) as f:
                        error_data = json.load(f)
                        error_type = error_data['error_type']
                        
                        # Count by severity
                        if 'CRITICAL' in error_data.get('level', ''):
                            error_counts['CRITICAL'] += 1
                        else:
                            error_counts['ERROR'] += 1
                            
                        # Count by type
                        error_types[error_type] = error_types.get(error_type, 0) + 1
                            
            return {
                'period_days': days,
                'total_errors': sum(error_counts.values()),
                'error_counts': error_counts,
                'error_types': error_types
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate error summary: {str(e)}")
            return {}