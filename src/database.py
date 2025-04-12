from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Veritabanı bağlantı URL'si
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Veritabanı motoru
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Oturum fabrikası
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Temel model sınıfı
Base = declarative_base()

# Veritabanı bağlantısı için bağımlılık
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 