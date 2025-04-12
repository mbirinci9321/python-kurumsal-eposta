from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class LogEntry(Base):
    """Log kaydı modeli."""
    
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # LOGIN, LOGOUT, CREATE, UPDATE, DELETE
    entity_type = Column(String)  # USER, TEMPLATE, LICENSE
    entity_id = Column(Integer)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    user = relationship("User", back_populates="logs") 