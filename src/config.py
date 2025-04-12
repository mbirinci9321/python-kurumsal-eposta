from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Uygulama ayarları
    APP_NAME: str = "Kurumsal E-posta İmza Yönetim Sistemi"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Veritabanı ayarları
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Active Directory ayarları
    AD_SERVER: str = "ldap://your-ad-server"
    AD_PORT: int = 389
    AD_BASE_DN: str = "DC=example,DC=com"
    AD_USERNAME: Optional[str] = None
    AD_PASSWORD: Optional[str] = None
    
    # Lisans ayarları
    LICENSE_KEY: Optional[str] = None
    LICENSE_TYPE: Optional[str] = None
    LICENSE_EXPIRY: Optional[str] = None
    
    # Log ayarları
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/app.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global ayarlar nesnesi
settings = Settings() 