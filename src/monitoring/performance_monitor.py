from typing import Dict, List, Optional
import time
from datetime import datetime
import logging
from dataclasses import dataclass
import threading
import psutil
import json

@dataclass
class PerformanceMetrics:
    timestamp: str
    operation: str
    duration_ms: float
    memory_usage_mb: float
    cpu_percent: float
    details: Dict

class PerformanceMonitor:
    """Monitor system performance and resource usage"""
    
    def __init__(self, log_file: str = 'performance.log'):
        self.logger = logging.getLogger('performance')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        self.metrics_history: List[PerformanceMetrics] = []
        self._lock = threading.Lock()
        
    def start_operation(self, operation: str) -> float:
        """Start timing an operation"""
        return time.time()
        
    def end_operation(self, start_time: float, operation: str, details: Dict = None) -> PerformanceMetrics:
        """End timing and record metrics"""
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            duration_ms=duration_ms,
            memory_usage_mb=self._get_memory_usage(),
            cpu_percent=self._get_cpu_usage(),
            details=details or {}
        )
        
        self._record_metrics(metrics)
        return metrics
        
    def get_metrics_summary(self) -> Dict:
        """Get summary of performance metrics"""
        with self._lock:
            if not self.metrics_history:
                return {}
                
            operations = {}
            for metric in self.metrics_history:
                if metric.operation not in operations:
                    operations[metric.operation] = []
                operations[metric.operation].append(metric.duration_ms)
                
            summary = {}
            for op, durations in operations.items():
                summary[op] = {
                    'avg_duration_ms': sum(durations) / len(durations),
                    'min_duration_ms': min(durations),
                    'max_duration_ms': max(durations),
                    'count': len(durations)
                }
                
            return summary
        
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
        
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent()
        
    def _record_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record metrics to log and history"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.logger.info(json.dumps({
                'timestamp': metrics.timestamp,
                'operation': metrics.operation,
                'duration_ms': metrics.duration_ms,
                'memory_usage_mb': metrics.memory_usage_mb,
                'cpu_percent': metrics.cpu_percent,
                'details': metrics.details
            }))