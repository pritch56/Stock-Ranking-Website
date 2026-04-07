from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import get_db
from models import Bot, Signal
from services import TradingEngine
from ws_manager import manager
from typing import Optional

router = APIRouter()


class SignalRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g. AAPL")
    action: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Number of units to trade")


class SignalResponse(BaseModel):
    success: bool
    trade_id: Optional[str] = None
    bot_name: Optional[str] = None
    ticker: Optional[str] = None
    action: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    value: Optional[float] = None
    timestamp: Optional[str] = None
    message: str


@router.post("/signal", response_model=SignalResponse)
async def submit_signal(
    signal: SignalRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Submit a trading signal.

    Send a JSON body with ticker, action, and quantity.
    Authenticate with your bot API key in the X-API-Key header.

    Example:
        POST /api/signal
        X-API-Key: <your-api-key>

        {
            "ticker": "AAPL",
            "action": "BUY",
            "quantity": 10
        }
    """

    bot = db.query(Bot).filter(Bot.api_key == api_key).first()
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not bot.is_active:
        raise HTTPException(status_code=403, detail="Bot is inactive")

    if signal.action.upper() not in ("BUY", "SELL"):
        raise HTTPException(status_code=400, detail="Action must be BUY or SELL")

    signal_record = Signal(
        bot_id=bot.id,
        ticker=signal.ticker.upper(),
        action=signal.action.upper(),
        quantity=signal.quantity
    )
    db.add(signal_record)
    db.commit()

    try:
        trading_engine = TradingEngine(db)
        result = await trading_engine.execute_signal(
            bot_id=bot.id,
            ticker=signal.ticker.upper(),
            action=signal.action.upper(),
            quantity=signal.quantity
        )

        signal_record.processed = "executed"
        db.commit()

        trade_event = {
            "trade_id": result["trade_id"],
            "bot_id": bot.id,
            "bot_name": bot.name,
            "ticker": result["ticker"],
            "action": result["action"].upper(),
            "quantity": result["quantity"],
            "price": result["price"],
            "value": result["value"],
            "timestamp": result["timestamp"]
        }

        await manager.broadcast({"type": "trade", "data": trade_event})

        return SignalResponse(
            success=True,
            trade_id=result["trade_id"],
            bot_name=bot.name,
            ticker=result["ticker"],
            action=result["action"].upper(),
            quantity=result["quantity"],
            price=result["price"],
            value=result["value"],
            timestamp=result["timestamp"],
            message="Trade executed successfully"
        )

    except Exception as e:
        signal_record.processed = "failed"
        signal_record.error_message = str(e)
        db.commit()

        return SignalResponse(success=False, message=f"Trade execution failed: {e}")


@router.get("/signal/history/{bot_id}")
async def get_signal_history(
    bot_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
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
