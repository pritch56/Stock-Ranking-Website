from sqlalchemy.orm import Session
from models import Bot, Trade, Signal, TradeAction
from config import settings
import random
from datetime import datetime, timezone

class TradingEngine:
    """Handles trade execution and simulation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.slippage_bps = settings.SLIPPAGE_BPS
        
    async def execute_signal(self, bot_id: str, ticker: str, action: str, quantity: float) -> dict:
        """Execute a trade signal from a bot"""
        
        # Validate bot
        bot = self.db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot or not bot.is_active:
            raise ValueError("Bot not found or inactive")
        
        # Get current market price
        price = await self.get_market_price(ticker)
        
        # Apply slippage
        slipped_price = self.apply_slippage(price, action)
        
        # Calculate trade value
        trade_value = slipped_price * quantity
        
        # Validate position size
        if trade_value > bot.current_capital * settings.MAX_POSITION_SIZE:
            raise ValueError("Trade size exceeds maximum position limit")
        
        # Create trade record
        trade = Trade(
            bot_id=bot_id,
            ticker=ticker,
            action=TradeAction.BUY if action.upper() == "BUY" else TradeAction.SELL,
            price=slipped_price,
            quantity=quantity,
            value=trade_value,
            slippage=slipped_price - price,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Update bot capital
        if action.upper() == "BUY":
            bot.current_capital -= trade_value
        else:
            bot.current_capital += trade_value
        
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        
        return {
            "trade_id": trade.id,
            "bot_id": bot_id,
            "ticker": ticker,
            "action": action,
            "price": slipped_price,
            "quantity": quantity,
            "value": trade_value,
            "timestamp": trade.timestamp.isoformat()
        }
    
    async def get_market_price(self, ticker: str) -> float:
        """Fetch current market price for ticker"""
        
        # For MVP, we'll simulate prices
        # In production, integrate with Polygon, Alpaca, or Yahoo Finance
        
        # Simulated price based on ticker
        base_prices = {
            "AAPL": 175.0,
            "GOOGL": 140.0,
            "MSFT": 380.0,
            "TSLA": 250.0,
            "AMZN": 170.0,
            "BTC": 45000.0,
            "ETH": 2500.0,
            "SPY": 450.0,
        }
        
        base_price = base_prices.get(ticker.upper(), 100.0)
        
        # Add random variation (+/- 2%)
        variation = random.uniform(-0.02, 0.02)
        price = base_price * (1 + variation)
        
        return round(price, 2)
    
    def apply_slippage(self, price: float, action: str) -> float:
        """Apply slippage to price based on trade direction"""
        
        slippage_factor = self.slippage_bps / 10000.0  # Convert basis points to decimal
        
        if action.upper() == "BUY":
            # Buying: pay more (slippage increases price)
            return round(price * (1 + slippage_factor), 2)
        else:
            # Selling: receive less (slippage decreases price)
            return round(price * (1 - slippage_factor), 2)
    
    def get_bot_positions(self, bot_id: str) -> dict:
        """Get current positions for a bot"""
        
        trades = self.db.query(Trade).filter(Trade.bot_id == bot_id).all()
        
        positions = {}
        for trade in trades:
            if trade.ticker not in positions:
                positions[trade.ticker] = {
                    "quantity": 0,
                    "total_cost": 0,
                    "avg_price": 0
                }
            
            if trade.action == TradeAction.BUY:
                positions[trade.ticker]["quantity"] += trade.quantity
                positions[trade.ticker]["total_cost"] += trade.value
            else:
                positions[trade.ticker]["quantity"] -= trade.quantity
                positions[trade.ticker]["total_cost"] -= trade.value
            
            # Calculate average price
            if positions[trade.ticker]["quantity"] > 0:
                positions[trade.ticker]["avg_price"] = (
                    positions[trade.ticker]["total_cost"] / positions[trade.ticker]["quantity"]
                )
        
        # Remove closed positions
        positions = {k: v for k, v in positions.items() if v["quantity"] != 0}
        
        return positions
