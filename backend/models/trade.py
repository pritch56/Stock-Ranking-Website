from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from database import Base
import uuid
import enum

class TradeAction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    ticker = Column(String, nullable=False, index=True)
    action = Column(Enum(TradeAction), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    value = Column(Float, nullable=False)  # price * quantity
    slippage = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Trade(bot_id={self.bot_id}, {self.action} {self.quantity} {self.ticker} @ {self.price})>"
