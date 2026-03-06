from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer
from sqlalchemy.sql import func
from database import Base

class Performance(Base):
    __tablename__ = "performance"
    
    id = Column(String, primary_key=True)  # Format: bot_id:period
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    period = Column(String, nullable=False, index=True)  # week, month, year, 5year
    
    # Performance Metrics
    total_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    
    # Trade Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # Capital
    initial_capital = Column(Float, default=100000.0)
    current_capital = Column(Float, default=100000.0)
    peak_capital = Column(Float, default=100000.0)
    
    # Timestamps
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Performance(bot_id={self.bot_id}, period={self.period}, return={self.total_return:.2%})>"
