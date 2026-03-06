from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid

class League(Base):
    __tablename__ = "leagues"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    strategy_type = Column(String, nullable=False)  # ML, HFT, Sentiment, Technical, Global
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<League(name={self.name}, strategy={self.strategy_type})>"
