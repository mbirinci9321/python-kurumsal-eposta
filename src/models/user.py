from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class User(Base):
    """Kullanıcı modeli."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    title = Column(String)
    department = Column(String)
    phone = Column(String)
    mobile = Column(String)
    manager_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # ADMIN, MANAGER, USER
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    manager = relationship("User", remote_side=[id], backref="subordinates")
    signature_templates = relationship("SignatureTemplate", back_populates="created_by")
    logs = relationship("LogEntry", back_populates="user") 