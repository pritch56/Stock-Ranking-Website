from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from database import Base
import uuid

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    ticker = Column(String, nullable=False)
    action = Column(String, nullable=False)  # BUY or SELL
    quantity = Column(Float, nullable=False)
    received_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed = Column(String, default="pending")  # pending, executed, failed
    error_message = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Signal(bot_id={self.bot_id}, {self.action} {self.ticker})>"
