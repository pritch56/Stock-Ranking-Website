from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from database import Base
import uuid
import secrets

class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    strategy_type = Column(String, nullable=False, index=True)  # ML, HFT, Sentiment, etc.
    description = Column(String)
    api_key = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    is_active = Column(Boolean, default=True)
    initial_capital = Column(Float, default=100000.0)
    current_capital = Column(Float, default=100000.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Bot(id={self.id}, name={self.name}, strategy={self.strategy_type})>"
