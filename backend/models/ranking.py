from sqlalchemy import Column, String, ForeignKey, Integer, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Ranking(Base):
    __tablename__ = "rankings"
    
    id = Column(String, primary_key=True)  # Format: league_id:bot_id:period
    league_id = Column(String, ForeignKey("leagues.id"), nullable=False, index=True)
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    period = Column(String, nullable=False, index=True)  # week, month, year, 5year
    
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # Risk-adjusted return
    previous_rank = Column(Integer)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Ranking(league={self.league_id}, bot={self.bot_id}, rank={self.rank})>"
