from typing import Dict, Optional
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration settings with validation"""
    env: str
    user_email: str
    api_key: Optional[str]
    rate_limit: int
    max_retries: int
    timeout: int
    cache_dir: Path
    log_level: str

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

def load_config(env_name: str = None) -> Config:
    """Load configuration from environment files"""
    # Determine environment
    env = env_name or os.getenv('APP_ENV', 'development')
    
    # Load base config first
    load_dotenv('.env')
    
    # Load environment-specific config
    env_file = f'.env.{env}'
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    
    try:
        config = Config(
            env=env,
            user_email=_get_required('USER_EMAIL'),
            api_key=os.getenv('API_KEY'),
            rate_limit=int(os.getenv('RATE_LIMIT', '3')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            timeout=int(os.getenv('TIMEOUT', '30')),
            cache_dir=Path(os.getenv('CACHE_DIR', 'cache')),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
        
        validate_config(config)
        return config
        
    except ValueError as e:
        raise ConfigError(f"Invalid configuration value: {str(e)}")

def validate_config(config: Config) -> None:
    """Validate configuration settings"""
    # Validate email format
    if '@' not in config.user_email:
        raise ConfigError("Invalid email format")
    
    # Validate rate limits
    if config.rate_limit < 1:
        raise ConfigError("Rate limit must be positive")
    
    if config.max_retries < 0:
        raise ConfigError("Max retries cannot be negative")
    
    # Validate timeout
    if config.timeout < 1:
        raise ConfigError("Timeout must be positive")
    
    # Ensure cache directory exists
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate log level
    valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    if config.log_level not in valid_log_levels:
        raise ConfigError(f"Invalid log level. Must be one of: {valid_log_levels}")

def _get_required(key: str) -> str:
    """Get required environment variable or raise error"""
    value = os.getenv(key)
    if not value:
        raise ConfigError(f"Missing required configuration: {key}")
    return value