from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, JSON
from sqlalchemy.orm import relationship

from ..database import Base

class License(Base):
    """Lisans modeli."""
    
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    type = Column(String)  # ENTERPRISE, DEPARTMENT, INDIVIDUAL
    start_date = Column(Date)
    end_date = Column(Date)
    max_users = Column(Integer)
    status = Column(String)  # ACTIVE, EXPIRED, SUSPENDED
    features = Column(JSON)  # Enabled features
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 