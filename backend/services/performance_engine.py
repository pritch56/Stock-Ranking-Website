from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Bot, Trade, Performance
from datetime import datetime, timedelta
import math

class PerformanceEngine:
    """Calculates performance metrics for bots"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_performance(self, bot_id: str, period: str) -> dict:
        """Calculate all performance metrics for a bot over a given period"""
        
        # Get period dates
        period_start, period_end = self.get_period_dates(period)
        
        # Get bot
        bot = self.db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise ValueError("Bot not found")
        
        # Get trades in period
        trades = self.db.query(Trade).filter(
            and_(
                Trade.bot_id == bot_id,
                Trade.timestamp >= period_start,
                Trade.timestamp <= period_end
            )
        ).order_by(Trade.timestamp).all()
        
        if not trades:
            return self.get_default_performance(bot_id, period)
        
        # Calculate metrics
        total_return = self.calculate_return(bot, trades)
        sharpe_ratio = self.calculate_sharpe_ratio(trades, bot.initial_capital)
        max_drawdown = self.calculate_max_drawdown(trades, bot.initial_capital)
        win_rate = self.calculate_win_rate(trades)
        
        # Trade statistics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if self.is_winning_trade(t, trades))
        losing_trades = total_trades - winning_trades
        
        # Save or update performance record
        performance_id = f"{bot_id}:{period}"
        performance = self.db.query(Performance).filter(Performance.id == performance_id).first()
        
        if not performance:
            performance = Performance(
                id=performance_id,
                bot_id=bot_id,
                period=period
            )
        
        performance.total_return = total_return
        performance.sharpe_ratio = sharpe_ratio
        performance.max_drawdown = max_drawdown
        performance.win_rate = win_rate
        performance.total_trades = total_trades
        performance.winning_trades = winning_trades
        performance.losing_trades = losing_trades
        performance.initial_capital = bot.initial_capital
        performance.current_capital = bot.current_capital
        performance.peak_capital = self.calculate_peak_capital(trades, bot.initial_capital)
        performance.period_start = period_start
        performance.period_end = period_end
        performance.updated_at = datetime.utcnow()
        
        self.db.merge(performance)
        self.db.commit()
        
        return {
            "bot_id": bot_id,
            "period": period,
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades
        }
    
    def calculate_return(self, bot: Bot, trades: list) -> float:
        """Calculate total return percentage"""
        if bot.initial_capital == 0:
            return 0.0
        
        return_pct = (bot.current_capital - bot.initial_capital) / bot.initial_capital
        return round(return_pct, 4)
    
    def calculate_sharpe_ratio(self, trades: list, initial_capital: float) -> float:
        """Calculate annualised Sharpe Ratio using daily net P&L as the return series"""
        from collections import defaultdict

        if len(trades) < 2:
            return 0.0

        daily_pnl: dict = defaultdict(float)
        for trade in trades:
            day = trade.timestamp.date()
            if trade.action.value == "SELL":
                daily_pnl[day] += trade.value
            else:
                daily_pnl[day] -= trade.value

        if len(daily_pnl) < 2:
            return 0.0

        returns = [pnl / initial_capital for pnl in daily_pnl.values()]
        mean_r = sum(returns) / len(returns)
        variance = sum((r - mean_r) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0.0

        return round((mean_r / std_dev) * math.sqrt(252), 2)
    
    def calculate_max_drawdown(self, trades: list, initial_capital: float) -> float:
        """Calculate maximum drawdown (largest peak-to-trough decline)"""
        
        if not trades:
            return 0.0
        
        capital = initial_capital
        peak = initial_capital
        max_dd = 0.0
        
        for trade in trades:
            if trade.action.value == "BUY":
                capital -= trade.value
            else:
                capital += trade.value
            
            # Update peak
            if capital > peak:
                peak = capital
            
            # Calculate drawdown
            drawdown = (peak - capital) / peak if peak > 0 else 0
            
            if drawdown > max_dd:
                max_dd = drawdown
        
        return round(max_dd, 4)
    
    def calculate_win_rate(self, trades: list) -> float:
        """Calculate win rate (percentage of profitable trades)"""
        
        if len(trades) < 2:
            return 0.0
        
        # For simplicity, we'll check pairs of buy/sell trades
        winning_trades = 0
        total_pairs = 0
        
        buy_trades = {}
        
        for trade in trades:
            ticker = trade.ticker
            
            if trade.action.value == "BUY":
                if ticker not in buy_trades:
                    buy_trades[ticker] = []
                buy_trades[ticker].append(trade)
            else:  # SELL
                if ticker in buy_trades and buy_trades[ticker]:
                    buy_trade = buy_trades[ticker].pop(0)
                    total_pairs += 1
                    
                    # Check if profitable
                    if trade.price > buy_trade.price:
                        winning_trades += 1
        
        if total_pairs == 0:
            return 0.0
        
        return round(winning_trades / total_pairs, 4)
    
    def calculate_peak_capital(self, trades: list, initial_capital: float) -> float:
        """Calculate peak capital reached"""
        
        capital = initial_capital
        peak = initial_capital
        
        for trade in trades:
            if trade.action.value == "BUY":
                capital -= trade.value
            else:
                capital += trade.value
            
            if capital > peak:
                peak = capital
        
        return peak
    
    def is_winning_trade(self, trade: Trade, all_trades: list) -> bool:
        """Check if a trade is profitable (simplified)"""
        # This is a simplified version
        # In production, you'd match buy/sell pairs properly
        return trade.action.value == "SELL"
    
    def get_period_dates(self, period: str):
        """Get start and end dates for a period"""
        
        end_date = datetime.utcnow()
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        elif period == "5year":
            start_date = end_date - timedelta(days=365*5)
        else:
            start_date = end_date - timedelta(days=30)  # Default to month
        
        return start_date, end_date
    
    def get_default_performance(self, bot_id: str, period: str) -> dict:
        """Return default performance when no trades exist"""
        return {
            "bot_id": bot_id,
            "period": period,
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0
        }
