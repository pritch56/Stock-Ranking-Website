"""Seed the database with sample bots, trades, and performance data."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uuid
import random
from datetime import datetime, timedelta, timezone

from database import SessionLocal
from models.user import User
from models.bot import Bot
from models.trade import Trade, TradeAction
from models.performance import Performance
from models.league import League
from models.ranking import Ranking
from services.leaderboard_engine import LeaderboardEngine

random.seed(42)

TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY', 'QQQ', 'NFLX']
BASE_PRICES = {
    'AAPL': 175.0, 'MSFT': 380.0, 'GOOGL': 140.0, 'AMZN': 170.0, 'TSLA': 250.0,
    'NVDA': 480.0, 'META': 370.0, 'SPY': 450.0, 'QQQ': 390.0, 'NFLX': 610.0,
}

BOTS = [
    # (name, strategy_type, monthly_return, sharpe, max_dd, win_rate, num_trades)
    ("AlphaNet v2",       "ML",         0.342, 2.41, 0.063, 0.72, 18),
    ("Neural Edge",       "ML",         0.225, 1.87, 0.092, 0.68, 22),
    ("DeepTrader Pro",    "ML",         0.187, 1.54, 0.118, 0.64, 15),
    ("QuantML Beta",      "ML",         0.083, 0.71, 0.141, 0.55, 12),
    ("Nexus AI",          "ML",        -0.021, -0.18, 0.198, 0.44, 10),

    ("FlashArb X",        "HFT",        0.289, 2.15, 0.047, 0.74, 48),
    ("LatencyZero",       "HFT",        0.192, 1.63, 0.071, 0.69, 56),
    ("MicroSpeed HFT",    "HFT",        0.156, 1.31, 0.088, 0.65, 62),
    ("TickSlayer",        "HFT",        0.113, 0.94, 0.105, 0.59, 44),
    ("PulseTrader",       "HFT",        0.047, 0.39, 0.134, 0.51, 38),

    ("Fibonacci Pro",     "Technical",  0.315, 2.28, 0.052, 0.71, 14),
    ("MACD Precision",    "Technical",  0.148, 1.22, 0.097, 0.63, 16),
    ("MovingAvgPro",      "Technical",  0.086, 0.72, 0.129, 0.56, 18),
    ("RSI Master",        "Technical",  0.069, 0.57, 0.145, 0.53, 12),
    ("BollingerBot",      "Technical", -0.018, -0.14, 0.187, 0.46, 10),

    ("SentimentAI",       "Sentiment",  0.164, 1.38, 0.093, 0.62, 20),
    ("NewsTrader Pro",    "Sentiment",  0.132, 1.09, 0.112, 0.58, 17),
    ("TweetAlgo",         "Sentiment",  0.091, 0.76, 0.138, 0.54, 14),
    ("MediaEdge",         "Sentiment",  0.078, 0.64, 0.152, 0.52, 11),
    ("SocialPulse",       "Sentiment", -0.053, -0.44, 0.221, 0.41, 9),

    ("CrossArb Elite",    "Arbitrage",  0.253, 1.98, 0.058, 0.70, 32),
    ("StatArb Prime",     "Arbitrage",  0.171, 1.42, 0.081, 0.66, 28),
    ("ConvergenceBot",    "Arbitrage",  0.129, 1.07, 0.103, 0.60, 24),
    ("DeltaNeutral",      "Arbitrage",  0.054, 0.45, 0.127, 0.53, 20),
    ("SpreadCapture",     "Arbitrage", -0.037, -0.31, 0.204, 0.43, 16),
]

DESCRIPTIONS = {
    "ML":         "Uses deep learning models to predict short-term price movements.",
    "HFT":        "High-frequency strategy exploiting micro-price inefficiencies.",
    "Technical":  "Signals derived from classic chart patterns and technical indicators.",
    "Sentiment":  "Combines social media and news sentiment with price action.",
    "Arbitrage":  "Statistical arbitrage across correlated equity pairs.",
}


def make_performance(bot_id: str, period: str, base_return: float, sharpe: float,
                     max_dd: float, win_rate: float, num_trades: int,
                     initial_capital: float) -> Performance:
    scale = {"week": 0.25, "month": 1.0, "year": 3.2, "5year": 6.5}[period]
    r = base_return * scale * random.uniform(0.85, 1.15)
    s = sharpe * scale ** 0.5 * random.uniform(0.85, 1.15)
    current = initial_capital * (1 + r)
    winning = round(num_trades * win_rate * scale)
    total = round(num_trades * scale)
    total = max(total, 2)
    winning = min(winning, total)

    now = datetime.now(timezone.utc)
    period_days = {"week": 7, "month": 30, "year": 365, "5year": 1825}[period]

    perf = Performance(
        id=f"{bot_id}:{period}",
        bot_id=bot_id,
        period=period,
        total_return=round(r, 4),
        sharpe_ratio=round(s, 2),
        max_drawdown=round(max_dd * random.uniform(0.8, 1.2), 4),
        win_rate=round(win_rate * random.uniform(0.9, 1.1), 4),
        total_trades=total,
        winning_trades=winning,
        losing_trades=total - winning,
        initial_capital=initial_capital,
        current_capital=round(current, 2),
        peak_capital=round(current * random.uniform(1.01, 1.08), 2),
        period_start=now - timedelta(days=period_days),
        period_end=now,
        updated_at=now,
    )
    return perf


def make_trades(bot_id: str, num_pairs: int, base_return: float) -> list[Trade]:
    now = datetime.now(timezone.utc)
    trades = []
    for _ in range(num_pairs):
        ticker = random.choice(TICKERS)
        base = BASE_PRICES[ticker]
        qty = round(random.uniform(5, 40), 0)
        days_ago = random.uniform(0.5, 29)
        buy_time = now - timedelta(days=days_ago + random.uniform(0.1, 1.5))
        sell_time = buy_time + timedelta(hours=random.uniform(1, 72))
        buy_price = round(base * random.uniform(0.96, 1.04), 2)
        # Profit factor derived from target return, with noise
        profit_factor = 1 + (base_return / max(num_pairs, 1)) * random.uniform(0.4, 2.0)
        sell_price = round(buy_price * profit_factor, 2)
        buy_value = round(buy_price * qty, 2)
        sell_value = round(sell_price * qty, 2)

        trades.append(Trade(
            id=str(uuid.uuid4()),
            bot_id=bot_id,
            ticker=ticker,
            action=TradeAction.BUY,
            price=buy_price,
            quantity=qty,
            value=buy_value,
            slippage=round(buy_price * 0.0005, 4),
            timestamp=buy_time,
        ))
        trades.append(Trade(
            id=str(uuid.uuid4()),
            bot_id=bot_id,
            ticker=ticker,
            action=TradeAction.SELL,
            price=sell_price,
            quantity=qty,
            value=sell_value,
            slippage=round(sell_price * 0.0005, 4),
            timestamp=sell_time,
        ))
    return trades


def run():
    db = SessionLocal()
    try:
        # Idempotency: use existing seed user or create one
        seed_user = db.query(User).filter(User.email == "seed@botleague.internal").first()
        if seed_user and db.query(Bot).filter(Bot.user_id == seed_user.id).count() >= len(BOTS):
            print("Seed data already present, skipping.")
            return

        if not seed_user:
            print("Creating seed user...")
            seed_user = User(id=str(uuid.uuid4()), email="seed@botleague.internal")
            db.add(seed_user)
            db.flush()
        else:
            print(f"Seed user exists (id={seed_user.id}), adding missing bots...")

        existing_names = {b.name for b in db.query(Bot).filter(Bot.user_id == seed_user.id).all()}
        print(f"Creating {len(BOTS)} bots with trades and performance records...")
        for name, strategy, monthly_ret, sharpe, max_dd, win_rate, num_trades in BOTS:
            if name in existing_names:
                continue

            initial_capital = 100_000.0
            current_capital = round(initial_capital * (1 + monthly_ret), 2)

            bot = Bot(
                id=str(uuid.uuid4()),
                user_id=seed_user.id,
                name=name,
                strategy_type=strategy,
                description=DESCRIPTIONS[strategy],
                initial_capital=initial_capital,
                current_capital=current_capital,
                is_active=True,
            )
            db.add(bot)
            db.flush()

            # Trades (used for the live feed)
            for t in make_trades(bot.id, num_trades // 2, monthly_ret):
                db.add(t)

            # Performance records for all periods
            for period in ("week", "month", "year", "5year"):
                db.merge(make_performance(
                    bot.id, period, monthly_ret, sharpe, max_dd, win_rate,
                    num_trades, initial_capital,
                ))

        db.commit()

        print("Ensuring leagues exist...")
        LeaderboardEngine(db).initialize_leagues()

        print("Computing rankings...")
        engine = LeaderboardEngine(db)
        for period in ("week", "month", "year", "5year"):
            engine.update_rankings(period)

        print("Seed complete.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run()
