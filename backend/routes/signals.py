from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Bot, Signal
from services import TradingEngine
from typing import Optional

router = APIRouter()

class SignalRequest(BaseModel):
    bot_id: str
    ticker: str
    action: str  # BUY or SELL
    quantity: float

class SignalResponse(BaseModel):
    success: bool
    trade_id: Optional[str] = None
    message: str
    details: Optional[dict] = None

@router.post("/signal", response_model=SignalResponse)
async def submit_signal(
    signal: SignalRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Submit a trading signal from a bot.
    
    Bots must include their API key in the X-API-Key header.
    """
    
    # Validate API key and bot
    bot = db.query(Bot).filter(
        Bot.id == signal.bot_id,
        Bot.api_key == api_key
    ).first()
    
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid bot_id or API key")
    
    if not bot.is_active:
        raise HTTPException(status_code=403, detail="Bot is inactive")
    
    # Validate signal
    if signal.action.upper() not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Action must be BUY or SELL")
    
    if signal.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    # Record signal
    signal_record = Signal(
        bot_id=signal.bot_id,
        ticker=signal.ticker,
        action=signal.action.upper(),
        quantity=signal.quantity
    )
    db.add(signal_record)
    db.commit()
    
    # Execute trade
    try:
        trading_engine = TradingEngine(db)
        trade_result = await trading_engine.execute_signal(
            bot_id=signal.bot_id,
            ticker=signal.ticker,
            action=signal.action,
            quantity=signal.quantity
        )
        
        # Update signal status
        signal_record.processed = "executed"
        db.commit()
        
        return SignalResponse(
            success=True,
            trade_id=trade_result["trade_id"],
            message="Trade executed successfully",
            details=trade_result
        )
        
    except Exception as e:
        # Mark signal as failed
        signal_record.processed = "failed"
        signal_record.error_message = str(e)
        db.commit()
        
        return SignalResponse(
            success=False,
            message=f"Trade execution failed: {str(e)}"
        )

@router.get("/signal/history/{bot_id}")
async def get_signal_history(
    bot_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get signal history for a bot"""
    
    signals = db.query(Signal).filter(
        Signal.bot_id == bot_id
    ).order_by(
        Signal.received_time.desc()
    ).limit(limit).all()
    
    return {
        "bot_id": bot_id,
        "total_signals": len(signals),
        "signals": [
            {
                "id": s.id,
                "ticker": s.ticker,
                "action": s.action,
                "quantity": s.quantity,
                "status": s.processed,
                "timestamp": s.received_time.isoformat()
            }
            for s in signals
        ]
    }
