from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services import LeaderboardEngine
from typing import Optional

router = APIRouter()

@router.get("/leaderboard")
async def get_leaderboard(
    period: str = Query("month", regex="^(week|month|year|5year)$"),
    league: str = Query("global", regex="^(global|ML|HFT|Sentiment|Technical|Arbitrage)$"),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for a specific period and league.
    
    - **period**: week, month, year, or 5year
    - **league**: global, ML, HFT, Sentiment, Technical, or Arbitrage
    - **limit**: Maximum number of results (default 100, max 1000)
    """
    
    leaderboard_engine = LeaderboardEngine(db)
    leaderboard = leaderboard_engine.get_leaderboard(
        period=period,
        league=league,
        limit=limit
    )
    
    return {
        "period": period,
        "league": league,
        "total_bots": len(leaderboard),
        "leaderboard": leaderboard
    }

@router.get("/leaderboard/top")
async def get_top_performers(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get top performing bots across all time"""
    
    leaderboard_engine = LeaderboardEngine(db)
    top_bots = leaderboard_engine.get_top_performers(limit=limit)
    
    return {
        "total": len(top_bots),
        "top_performers": top_bots
    }

@router.get("/leaderboard/bot/{bot_id}")
async def get_bot_rankings(
    bot_id: str,
    period: str = "month",
    db: Session = Depends(get_db)
):
    """Get ranking information for a specific bot"""
    
    leaderboard_engine = LeaderboardEngine(db)
    rankings = leaderboard_engine.get_bot_ranking(bot_id, period)
    
    return rankings

@router.post("/leaderboard/update")
async def update_leaderboard(
    period: str = "month",
    db: Session = Depends(get_db)
):
    """
    Manually trigger leaderboard update for a period.
    This is typically run by a background worker.
    """
    
    leaderboard_engine = LeaderboardEngine(db)
    leaderboard_engine.update_rankings(period)
    
    return {
        "success": True,
        "message": f"Leaderboard updated for period: {period}"
    }

@router.get("/leagues")
async def list_leagues(db: Session = Depends(get_db)):
    """List all available leagues"""
    
    from models import League
    leagues = db.query(League).all()
    
    return {
        "total": len(leagues),
        "leagues": [
            {
                "id": l.id,
                "name": l.name,
                "strategy_type": l.strategy_type,
                "description": l.description
            }
            for l in leagues
        ]
    }
