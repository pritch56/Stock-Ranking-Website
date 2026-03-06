# Trading Bot League Platform

A complete production-ready web platform for algorithmic trading bot competitions. Bots compete in performance leagues with real-time rankings, performance analytics, and trade execution.

## 🚀 Features

### Core Features
- **Bot Registration** - Create and manage multiple trading bots
- **Signal API** - Submit trade signals via REST API
- **Simulated Trading** - Fair execution with price slippage modeling
- **Performance Analytics** - Return, Sharpe Ratio, Max Drawdown, Win Rate
- **League System** - Compete in strategy-specific leagues (ML, HFT, Sentiment, Technical, Arbitrage)
- **Real-time Leaderboards** - Live rankings with WebSocket updates
- **Interactive Charts** - Equity curves, performance visualization
- **Dashboard** - Manage bots, view trades, track performance

### Technical Features
- **FastAPI Backend** - High-performance async Python API
- **PostgreSQL Database** - Reliable data storage via Supabase
- **WebSocket Support** - Real-time updates
- **Redis Caching** - Fast leaderboard queries
- **Background Workers** - Automated performance calculations
- **Docker Deployment** - Easy containerized setup
- **Modern UI** - Animated, responsive frontend with TailwindCSS

## 📋 Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **Cache**: Redis
- **Workers**: Celery/Python
- **Server**: Uvicorn

### Frontend
- **HTML5** with semantic markup
- **TailwindCSS** for styling
- **Vanilla JavaScript** for interactivity
- **Chart.js** for data visualization
- **Particles.js** for animated backgrounds
- **WebSocket** for real-time updates

### Infrastructure
- **Docker** & Docker Compose
- **Nginx** for reverse proxy
- **PostgreSQL** database
- **Redis** message broker

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (or use Supabase)
- Redis

### Quick Start with Docker

1. **Clone the repository**
```powershell
cd c:\Stock-Ranking-Website
```

2. **Configure environment variables**
```powershell
cp backend\.env.example backend\.env
# Edit backend\.env with your configuration
```

3. **Start all services**
```powershell
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

1. **Create virtual environment**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
```

3. **Configure environment**
```powershell
cp .env.example .env
# Edit .env with your database and API credentials
```

4. **Run the backend**
```powershell
python main.py
```

#### Frontend Setup

The frontend is static HTML/CSS/JS. Simply open `frontend/index.html` in a browser or serve via a local server:

```powershell
cd frontend
python -m http.server 8080
```

Then access: http://localhost:8080

## 📊 Database Schema

### Tables
- **users** - User accounts
- **bots** - Trading bot profiles
- **trades** - Executed trades
- **signals** - Incoming trade signals
- **performance** - Performance metrics by period
- **leagues** - Strategy leagues
- **rankings** - Bot rankings per league

## 🔌 API Documentation

### Authentication
Bots authenticate using API keys sent in the `X-API-Key` header.

### Core Endpoints

#### Submit Trade Signal
```http
POST /api/signal
X-API-Key: your-bot-api-key

{
  "bot_id": "bot-uuid",
  "ticker": "AAPL",
  "action": "BUY",
  "quantity": 10.0
}
```

#### Create Bot
```http
POST /api/bots

{
  "user_id": "user-uuid",
  "name": "My Trading Bot",
  "strategy_type": "ML",
  "description": "Machine learning based strategy",
  "initial_capital": 100000.0
}
```

#### Get Leaderboard
```http
GET /api/leaderboard?period=month&league=global&limit=100
```

#### Get Bot Performance
```http
GET /api/bot/{bot_id}/performance?period=month
```

Full API documentation available at: http://localhost:8000/docs

## 🤖 Bot Integration Guide

### Python Example

```python
import requests

API_URL = "http://localhost:8000/api"
BOT_ID = "your-bot-id"
API_KEY = "your-api-key"

# Submit a trade signal
def submit_trade(ticker, action, quantity):
    headers = {
        "X-API-Key": API_KEY
    }
    data = {
        "bot_id": BOT_ID,
        "ticker": ticker,
        "action": action,  # "BUY" or "SELL"
        "quantity": quantity
    }
    
    response = requests.post(
        f"{API_URL}/signal",
        json=data,
        headers=headers
    )
    
    return response.json()

# Example: Buy 10 shares of AAPL
result = submit_trade("AAPL", "BUY", 10.0)
print(result)
```

## 🏆 League System

Bot compete in multiple leagues simultaneously:

- **Global League** - All bots compete together
- **ML League** - Machine learning strategies
- **HFT League** - High frequency trading
- **Sentiment League** - Sentiment analysis based
- **Technical League** - Technical analysis strategies
- **Arbitrage League** - Arbitrage strategies

Rankings are calculated for multiple time periods:
- Weekly
- Monthly
- Yearly
- 5-Year

## 📈 Performance Metrics

### Calculated Metrics
- **Total Return** - % gain/loss from initial capital
- **Sharpe Ratio** - Risk-adjusted return
- **Max Drawdown** - Largest peak-to-trough decline
- **Win Rate** - % of profitable trades
- **Total Trades** - Number of executed trades

### Ranking Score
Bots are ranked by a weighted score:
```
Score = (Return × 0.6) + (Sharpe Ratio / 10 × 0.4)
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/botleague

# Supabase (optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Redis
REDIS_URL=redis://localhost:6379

# Trading
INITIAL_CAPITAL=100000.0
MAX_POSITION_SIZE=1.0
SLIPPAGE_BPS=5.0

# Market Data (optional)
POLYGON_API_KEY=your-key
ALPACA_API_KEY=your-key
```

## 🎨 Frontend Pages

- **Landing Page** (`index.html`) - Hero section, features, leaderboard preview
- **Leaderboard** (`leaderboard.html`) - Full rankings with filters
- **Dashboard** (`dashboard.html`) - User control center
- **Bot Profile** (`bot.html`) - Detailed bot analytics

## 🚀 Deployment

### Production Considerations

1. **Environment Variables** - Set secure keys
2. **Database** - Use managed PostgreSQL (Supabase recommended)
3. **SSL/TLS** - Enable HTTPS
4. **Rate Limiting** - Configure appropriate limits
5. **Monitoring** - Set up logging and alerting
6. **Backups** - Regular database backups

### Deployment Options

- **Vercel** (Frontend)
- **Fly.io** or **AWS EC2** (Backend)
- **Supabase** (Database)
- **Cloudflare** (CDN)

## 📝 Development Roadmap

### Phase 1 - MVP (Current)
- [x] User accounts
- [x] Bot registration
- [x] Signal API
- [x] Simulated trading
- [x] Performance metrics
- [x] Leaderboards
- [x] Basic UI

### Phase 2 - Enhancements
- [ ] Real broker integration (Alpaca, IB)
- [ ] Advanced charts
- [ ] Strategy marketplace
- [ ] Social features
- [ ] Mobile app

### Phase 3 - Scale
- [ ] Copy trading
- [ ] AI ranking
- [ ] Public API
- [ ] White-label solution

## 🤝 Contributing

Contributions welcome! Please read the contributing guidelines before submitting PRs.

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

For support, email support@tradingbotleague.com or open an issue.

## 🙏 Acknowledgments

Built with:
- FastAPI
- SQLAlchemy
- Chart.js
- TailwindCSS
- Particles.js

---

**Built with ❤️ for algorithmic trading enthusiasts**
