# Example Trading Bot

A minimal moving-average crossover bot that submits live trade signals to the Trading Bot League platform.

## Quick start

```bash
cd example_bot
pip install -r requirements.txt
python bot.py
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` | off | Print signals without submitting them |
| `--interval N` | `10` | Seconds between ticks |
| `--tickers A B …` | AAPL MSFT GOOGL TSLA NVDA | Tickers to trade |

## Examples

```bash
# Run normally (trades every 10 s)
python bot.py

# Test the strategy without submitting trades
python bot.py --dry-run

# Trade faster and on fewer symbols
python bot.py --interval 5 --tickers AAPL TSLA

# Trade once per minute across all default tickers
python bot.py --interval 60
```

## Strategy

Dual moving-average crossover:

- Maintains a **short window** (5 ticks) and a **long window** (20 ticks) per ticker.
- **BUY** when the short MA crosses above the long MA (no open position).
- **SELL** when the short MA crosses below the long MA (position open).

Price data is simulated locally with a slow random walk. The server applies its own slippage model when the signal is received.

## API reference

```
POST http://localhost:8000/api/signal
X-API-Key: <your-api-key>
Content-Type: application/json

{ "ticker": "AAPL", "action": "BUY", "quantity": 10 }
```

Response:

```json
{
  "success": true,
  "trade_id": "...",
  "ticker": "AAPL",
  "action": "BUY",
  "quantity": 10,
  "price": 175.88,
  "value": 1758.8,
  "timestamp": "2026-04-08T21:00:00Z",
  "message": "Trade executed successfully"
}
```

## Configuration

Edit the constants at the top of `bot.py`:

```python
API_KEY      = "ktKoBtX58ujptTA2r3eFJ1nji0Ahk5BVmC6WblYMsPo"
BASE_URL     = "http://localhost:8000/api"
SHORT_WINDOW = 5
LONG_WINDOW  = 20
QUANTITY     = 10
```
