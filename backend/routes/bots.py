from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from database import get_db
from models import Bot, Trade, Performance
from services import PerformanceEngine, TradingEngine
from typing import Optional, List
from datetime import datetime

router = APIRouter()

class CreateBotRequest(BaseModel):
    user_id: str
    name: str
    strategy_type: str
    description: Optional[str] = None
    initial_capital: float = 100000.0

class BotResponse(BaseModel):
    bot_id: str
    name: str
    strategy_type: str
    api_key: str
    initial_capital: float
    current_capital: float
    created_at: str

@router.post("/bots", response_model=BotResponse)
async def create_bot(
    bot_request: CreateBotRequest,
    db: Session = Depends(get_db)
):
    """Create a new trading bot"""
    
    # Validate strategy type
    valid_strategies = ["ML", "HFT", "Sentiment", "Technical", "Arbitrage", "Custom"]
    if bot_request.strategy_type not in valid_strategies:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy type. Must be one of: {', '.join(valid_strategies)}"
        )
    
    # Create bot
    bot = Bot(
        user_id=bot_request.user_id,
        name=bot_request.name,
        strategy_type=bot_request.strategy_type,
        description=bot_request.description,
        initial_capital=bot_request.initial_capital,
        current_capital=bot_request.initial_capital
    )
    
    db.add(bot)
    db.commit()
    db.refresh(bot)
    
    return BotResponse(
        bot_id=bot.id,
        name=bot.name,
        strategy_type=bot.strategy_type,
        api_key=bot.api_key,
        initial_capital=bot.initial_capital,
        current_capital=bot.current_capital,
        created_at=bot.created_at.isoformat()
    )

@router.get("/bots/{bot_id}")
async def get_bot(bot_id: str, db: Session = Depends(get_db)):
    """Get bot details"""
    
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {
        "bot_id": bot.id,
        "name": bot.name,
        "strategy_type": bot.strategy_type,
        "description": bot.description,
        "initial_capital": bot.initial_capital,
        "current_capital": bot.current_capital,
        "is_active": bot.is_active,
        "created_at": bot.created_at.isoformat()
    }

@router.get("/bots/{bot_id}/performance")
async def get_bot_performance(
    bot_id: str,
    period: str = "month",
    db: Session = Depends(get_db)
):
    """Get performance metrics for a bot"""
    
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Calculate performance
    performance_engine = PerformanceEngine(db)
    performance = performance_engine.calculate_performance(bot_id, period)
    
    return performance

@router.get("/bots/{bot_id}/trades")
async def get_bot_trades(
    bot_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trade history for a bot"""
    
    trades = db.query(Trade).filter(
        Trade.bot_id == bot_id
    ).order_by(
        Trade.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "bot_id": bot_id,
        "total_trades": len(trades),
        "trades": [
            {
                "id": t.id,
                "ticker": t.ticker,
                "action": t.action.value,
                "price": t.price,
                "quantity": t.quantity,
                "value": t.value,
                "timestamp": t.timestamp.isoformat()
            }
            for t in trades
        ]
    }

@router.get("/bots/{bot_id}/positions")
async def get_bot_positions(
    bot_id: str,
    db: Session = Depends(get_db)
):
    """Get current positions for a bot"""
    
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    trading_engine = TradingEngine(db)
    positions = trading_engine.get_bot_positions(bot_id)
    
    return {
        "bot_id": bot_id,
        "current_capital": bot.current_capital,
        "positions": positions
    }

@router.get("/bots")
async def list_bots(
    user_id: Optional[str] = None,
    strategy_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List bots with optional filters"""
    
    query = db.query(Bot)
    
    if user_id:
        query = query.filter(Bot.user_id == user_id)
    
    if strategy_type:
        query = query.filter(Bot.strategy_type == strategy_type)
    
    bots = query.limit(limit).all()
    
    return {
        "total": len(bots),
        "bots": [
            {
                "bot_id": b.id,
                "name": b.name,
                "strategy_type": b.strategy_type,
                "current_capital": b.current_capital,
                "is_active": b.is_active,
                "created_at": b.created_at.isoformat()
            }
            for b in bots
        ]
    }

@router.get("/trades/live")
async def get_live_trades(limit: int = 20, db: Session = Depends(get_db)):
    """
    Recent trades across all bots, newest first.
    Used by the live feed on the homepage and dashboard.
    """
    results = db.query(Trade, Bot).join(
        Bot, Bot.id == Trade.bot_id
    ).order_by(
        desc(Trade.timestamp)
    ).limit(limit).all()

    return {
        "trades": [
            {
                "trade_id": trade.id,
                "bot_id": bot.id,
                "bot_name": bot.name,
                "ticker": trade.ticker,
                "action": trade.action.value,
                "quantity": trade.quantity,
                "price": trade.price,
                "value": trade.value,
                "timestamp": trade.timestamp.isoformat()
            }
            for trade, bot in results
        ]
    }


@router.patch("/bots/{bot_id}/activate")
async def activate_bot(bot_id: str, db: Session = Depends(get_db)):
    """Activate a bot"""
    
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot.is_active = True
    db.commit()
    
    return {"message": "Bot activated", "bot_id": bot_id}

@router.patch("/bots/{bot_id}/deactivate")
async def deactivate_bot(bot_id: str, db: Session = Depends(get_db)):
    """Deactivate a bot"""
    
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot.is_active = False
    db.commit()
    
    return {"message": "Bot deactivated", "bot_id": bot_id}
