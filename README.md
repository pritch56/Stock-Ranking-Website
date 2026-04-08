# Trading Bot League

A web platform for algorithmic trading bot competitions. Bots compete in performance leagues with real-time rankings, analytics, and simulated trade execution.

---

## Running the Project

### Docker (recommended)

Requires Docker and Docker Compose.

```bash
docker-compose up -d
```

This starts PostgreSQL, Redis, the FastAPI backend, a performance worker, and an Nginx frontend server.

| Service     | URL                                      |
|-------------|------------------------------------------|
| Frontend    | <http://localhost>                       |
| Backend API | <http://localhost:8000>                  |
| API docs    | <http://localhost:8000/docs>             |

Before starting in production, change the hardcoded credentials in `docker-compose.yml` (`POSTGRES_PASSWORD`, `SECRET_KEY`).

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in DATABASE_URL, REDIS_URL, SECRET_KEY
uvicorn main:app --reload
```

The API will be available at <http://localhost:8000>.

#### Frontend

The frontend is static HTML/CSS/JS. Serve it with any local server:

```bash
cd frontend
python -m http.server 8080
```

Then open <http://localhost:8080>.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and set the following:

| Variable          | Description                             |
|-------------------|-----------------------------------------|
| `DATABASE_URL`    | PostgreSQL connection string            |
| `REDIS_URL`       | Redis connection string                 |
| `SECRET_KEY`      | Secret key for session signing          |
| `SUPABASE_URL`    | Supabase project URL (optional)         |
| `SUPABASE_KEY`    | Supabase anon key (optional)            |
| `POLYGON_API_KEY` | Polygon.io market data key (optional)   |
| `ALPACA_API_KEY`  | Alpaca market data key (optional)       |

---

## Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Redis, Uvicorn
- **Frontend:** HTML5, TailwindCSS, Vanilla JS, Chart.js, Particles.js
- **Infrastructure:** Docker Compose, Nginx

---

## API Reference

Bots authenticate with an API key in the `X-API-Key` header.

### Submit a trade signal

```http
POST /api/signal
X-API-Key: <bot-api-key>
Content-Type: application/json

{
  "bot_id": "<uuid>",
  "ticker": "AAPL",
  "action": "BUY",
  "quantity": 10.0
}
```

### Create a bot

```http
POST /api/bots
Content-Type: application/json

{
  "user_id": "<uuid>",
  "name": "My Bot",
  "strategy_type": "ML",
  "description": "Machine learning strategy",
  "initial_capital": 100000.0
}
```

### Leaderboard

```http
GET /api/leaderboard?period=month&league=global&limit=100
```

### Bot performance

```http
GET /api/bot/<bot_id>/performance?period=month
```

Full interactive docs at <http://localhost:8000/docs>.

---

## Python Client Example

```python
import requests

API_URL = "http://localhost:8000/api"
BOT_ID = "your-bot-id"
API_KEY = "your-api-key"

def submit_signal(ticker, action, quantity):
    return requests.post(
        f"{API_URL}/signal",
        json={"bot_id": BOT_ID, "ticker": ticker, "action": action, "quantity": quantity},
        headers={"X-API-Key": API_KEY},
    ).json()

result = submit_signal("AAPL", "BUY", 10.0)
```

---

## League System

Bots are ranked across multiple leagues and time periods.

- **Leagues:** Global, ML, HFT, Sentiment, Technical, Arbitrage
- **Periods:** Weekly, Monthly, Yearly, 5-Year
- **Metrics:** Total return, Sharpe ratio, max drawdown, win rate, trade count

Ranking score:

```
Score = (Total Return × 0.6) + (Sharpe Ratio / 10 × 0.4)
```

---

## Database Schema

| Table         | Description                    |
|---------------|--------------------------------|
| `users`       | User accounts                  |
| `bots`        | Bot profiles                   |
| `trades`      | Executed trades                |
| `signals`     | Incoming trade signals         |
| `performance` | Metrics by bot and period      |
| `leagues`     | Strategy leagues               |
| `rankings`    | Bot rankings per league        |

---

## Frontend Pages

| File               | Purpose                                   |
|--------------------|-------------------------------------------|
| `index.html`       | Landing page with leaderboard preview     |
| `leaderboard.html` | Full rankings with filters                |
| `dashboard.html`   | User and bot management                   |
| `bot.html`         | Per-bot analytics and trade history       |

---

## Licence

Proprietary. All rights reserved.
