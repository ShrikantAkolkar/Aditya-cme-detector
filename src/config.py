import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def database_url(self) -> str:
        return os.getenv('DATABASE_URL', self.get('database.url'))
    
    @property
    def redis_url(self) -> str:
        return os.getenv('REDIS_URL', self.get('redis.url'))
    
    @property
    def twilio_account_sid(self) -> str:
        return os.getenv('TWILIO_ACCOUNT_SID')
    
    @property
    def twilio_auth_token(self) -> str:
        return os.getenv('TWILIO_AUTH_TOKEN')
    
    @property
    def twilio_phone_number(self) -> str:
        return os.getenv('TWILIO_PHONE_NUMBER')
    
    @property
    def email_host(self) -> str:
        return os.getenv('EMAIL_HOST', self.get('alerts.email.smtp_server'))
    
    @property
    def email_port(self) -> int:
        return int(os.getenv('EMAIL_PORT', self.get('alerts.email.smtp_port', 587)))
    
    @property
    def email_user(self) -> str:
        return os.getenv('EMAIL_USER')
    
    @property
    def email_password(self) -> str:
        return os.getenv('EMAIL_PASSWORD')

# Global configuration instance
config = Config()