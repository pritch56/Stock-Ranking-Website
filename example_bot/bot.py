"""
Example trading bot for Trading Bot League.

Submits BUY/SELL signals to the platform API using a simple
moving-average crossover strategy on simulated price data.

Usage:
    python bot.py                  # run with default settings
    python bot.py --dry-run        # print signals without submitting
    python bot.py --interval 30    # trade every 30 seconds
"""

import argparse
import time
import random
import requests
from collections import deque
from datetime import datetime, timezone

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY   = "ktKoBtX58ujptTA2r3eFJ1nji0Ahk5BVmC6WblYMsPo"
BASE_URL  = "http://localhost:8000/api"

# Tickers this bot will trade
TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

# Moving-average windows (in ticks)
SHORT_WINDOW = 5
LONG_WINDOW  = 20

# Fixed quantity per trade
QUANTITY = 10

# Simulated base prices (the server also simulates; this is for local strategy logic)
BASE_PRICES = {
    "AAPL":  175.0,
    "MSFT":  380.0,
    "GOOGL": 140.0,
    "TSLA":  250.0,
    "NVDA":  480.0,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def fetch_price(ticker: str) -> float:
    """Return a locally-simulated price (±2 % noise around a drifting base)."""
    base = BASE_PRICES[ticker]
    # Slow random walk so the price actually moves over time
    drift = random.gauss(0, 0.003)
    BASE_PRICES[ticker] = round(base * (1 + drift), 2)
    noise = random.uniform(-0.01, 0.01)
    return round(BASE_PRICES[ticker] * (1 + noise), 2)


def submit_signal(ticker: str, action: str, quantity: int, dry_run: bool) -> dict | None:
    """POST a trade signal to the platform."""
    payload = {"ticker": ticker, "action": action, "quantity": quantity}

    if dry_run:
        log(f"[DRY RUN] {action} {quantity} {ticker}")
        return None

    try:
        resp = requests.post(
            f"{BASE_URL}/signal",
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        log(f"HTTP error submitting signal: {e.response.status_code} {e.response.text}")
    except requests.RequestException as e:
        log(f"Network error: {e}")
    return None


def moving_average(prices: deque) -> float:
    return sum(prices) / len(prices)


# ── Strategy ──────────────────────────────────────────────────────────────────

class MACrossoverBot:
    """
    Simple dual moving-average crossover.

    Signal logic:
      - Short MA crosses above Long MA  → BUY
      - Short MA crosses below Long MA  → SELL (if holding)
    """

    def __init__(self, tickers: list[str], dry_run: bool):
        self.dry_run  = dry_run
        self.tickers  = tickers
        self.prices   = {t: deque(maxlen=LONG_WINDOW) for t in tickers}
        self.position = {t: False for t in tickers}  # True = holding

    def tick(self, ticker: str) -> None:
        price = fetch_price(ticker)
        self.prices[ticker].append(price)

        if len(self.prices[ticker]) < LONG_WINDOW:
            log(f"{ticker} @ {price:.2f}  (warming up {len(self.prices[ticker])}/{LONG_WINDOW})")
            return

        short_ma = moving_average(list(self.prices[ticker])[-SHORT_WINDOW:])
        long_ma  = moving_average(self.prices[ticker])

        log(f"{ticker} @ {price:.2f}  short_ma={short_ma:.2f}  long_ma={long_ma:.2f}")

        if short_ma > long_ma and not self.position[ticker]:
            result = submit_signal(ticker, "BUY", QUANTITY, self.dry_run)
            if result or self.dry_run:
                self.position[ticker] = True
                if result:
                    log(f"  ✓ BUY filled  trade_id={result.get('trade_id')}  price={result.get('price')}")

        elif short_ma < long_ma and self.position[ticker]:
            result = submit_signal(ticker, "SELL", QUANTITY, self.dry_run)
            if result or self.dry_run:
                self.position[ticker] = False
                if result:
                    log(f"  ✓ SELL filled trade_id={result.get('trade_id')}  price={result.get('price')}")

    def run(self, interval: float) -> None:
        log(f"Bot started  tickers={self.tickers}  interval={interval}s  dry_run={self.dry_run}")
        log(f"API endpoint: {BASE_URL}")
        log("-" * 60)

        while True:
            for ticker in self.tickers:
                self.tick(ticker)
            time.sleep(interval)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="MA-crossover trading bot")
    parser.add_argument("--dry-run",  action="store_true", help="Print signals without submitting")
    parser.add_argument("--interval", type=float, default=10.0,  help="Seconds between ticks (default: 10)")
    parser.add_argument("--tickers",  nargs="+",  default=TICKERS, help="Tickers to trade")
    args = parser.parse_args()

    bot = MACrossoverBot(tickers=args.tickers, dry_run=args.dry_run)
    try:
        bot.run(interval=args.interval)
    except KeyboardInterrupt:
        log("Stopped.")


if __name__ == "__main__":
    main()
