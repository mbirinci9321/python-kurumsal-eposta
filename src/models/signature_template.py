from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ..database import Base

class SignatureTemplate(Base):
    """İmza şablonu modeli."""
    
    __tablename__ = "signature_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    content = Column(String)  # HTML content
    department = Column(String)
    is_default = Column(Boolean, default=False)
    variables = Column(JSON)  # Available template variables
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    created_by = relationship("User", back_populates="signature_templates") 