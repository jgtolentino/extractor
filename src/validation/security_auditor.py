from typing import Dict, List, Optional
import logging
from datetime import datetime
import hashlib
import json
from dataclasses import dataclass

@dataclass
class SecurityAuditResult:
    timestamp: str
    action: str
    user: str
    status: str
    details: Dict
    risk_level: str

class SecurityAuditor:
    """Monitor and audit security-related events"""
    
    def __init__(self, log_file: str = 'security_audit.log'):
        self.logger = logging.getLogger('security_audit')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def audit_search(self, query: str, user: str, ip_address: str) -> SecurityAuditResult:
        """Audit search operation"""
        risk_level = self._assess_search_risk(query)
        
        result = SecurityAuditResult(
            timestamp=datetime.now().isoformat(),
            action='search',
            user=user,
            status='completed',
            details={
                'query': query,
                'ip_address': ip_address,
                'query_hash': self._hash_query(query)
            },
            risk_level=risk_level
        )
        
        self._log_audit(result)
        return result
        
    def audit_export(self, user: str, export_format: str, file_path: str) -> SecurityAuditResult:
        """Audit data export operation"""
        result = SecurityAuditResult(
            timestamp=datetime.now().isoformat(),
            action='export',
            user=user,
            status='completed',
            details={
                'format': export_format,
                'file_path': file_path,
                'file_hash': self._hash_file(file_path)
            },
            risk_level='low'
        )
        
        self._log_audit(result)
        return result
        
    def audit_api_access(self, endpoint: str, user: str, ip_address: str) -> SecurityAuditResult:
        """Audit API access"""
        risk_level = self._assess_api_risk(endpoint, user)
        
        result = SecurityAuditResult(
            timestamp=datetime.now().isoformat(),
            action='api_access',
            user=user,
            status='completed',
            details={
                'endpoint': endpoint,
                'ip_address': ip_address,
                'access_type': self._get_access_type(endpoint)
            },
            risk_level=risk_level
        )
        
        self._log_audit(result)
        return result
        
    def _assess_search_risk(self, query: str) -> str:
        """Assess risk level of search query"""
        risk_indicators = [
            'password', 'token', 'key', 'secret', 'credential',
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP'
        ]
        
        query_lower = query.lower()
        if any(indicator.lower() in query_lower for indicator in risk_indicators):
            return 'high'
        elif len(query) > 500:
            return 'medium'
        return 'low'
        
    def _assess_api_risk(self, endpoint: str, user: str) -> str:
        """Assess risk level of API access"""
        high_risk_endpoints = ['admin', 'config', 'security', 'user']
        if any(endpoint.startswith(e) for e in high_risk_endpoints):
            return 'high'
        return 'low'
        
    def _hash_query(self, query: str) -> str:
        """Create hash of search query"""
        return hashlib.sha256(query.encode()).hexdigest()
        
    def _hash_file(self, file_path: str) -> str:
        """Create hash of exported file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to hash file {file_path}: {str(e)}")
            return ''
            
    def _get_access_type(self, endpoint: str) -> str:
        """Determine API access type"""
        if endpoint.startswith('read'):
            return 'read'
        elif endpoint.startswith('write'):
            return 'write'
        return 'unknown'
        
    def _log_audit(self, result: SecurityAuditResult) -> None:
        """Log audit result"""
        log_entry = {
            'timestamp': result.timestamp,
            'action': result.action,
            'user': result.user,
            'status': result.status,
            'details': result.details,
            'risk_level': result.risk_level
        }
        
        self.logger.info(json.dumps(log_entry))