# Setup Guide - Trading Bot League Platform

Complete step-by-step guide to get the platform running locally.

## Prerequisites Check

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] Text editor (VS Code recommended)
- [ ] Web browser (Chrome/Firefox recommended)

## Step 1: Project Setup

### 1.1 Navigate to Project Directory
```powershell
cd c:\Stock-Ranking-Website
```

### 1.2 Verify Project Structure
```powershell
Get-ChildItem -Recurse -Depth 1
```

You should see:
```
backend/
  - main.py
  - config.py
  - models/
  - routes/
  - services/
  - workers/
frontend/
  - index.html
  - leaderboard.html
  - dashboard.html
  - bot.html
  - css/
  - js/
docker-compose.yml
README.md
```

## Step 2: Configure Environment

### 2.1 Create Environment File
```powershell
cd backend
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}
notepad .env
```

### 2.2 Edit Configuration
Update the following in `.env`:

```env
# Database
DATABASE_URL=postgresql://botleague_user:changeme_in_production@db:5432/botleague

# Security (CHANGE THIS!)
SECRET_KEY=your-very-secure-random-string-change-this

# Redis
REDIS_URL=redis://redis:6379

# Trading Settings
INITIAL_CAPITAL=100000.0
MAX_POSITION_SIZE=1.0
SLIPPAGE_BPS=5.0
```

## Step 3: Start with Docker (Recommended)

### 3.1 Start All Services
```powershell
cd c:\Stock-Ranking-Website
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- Backend API on port 8000
- Performance worker (background)
- Frontend on port 80

### 3.2 Check Status
```powershell
docker-compose ps
```

All services should show "Up" status.

### 3.3 View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### 3.4 Access the Platform

Open your browser:
- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Step 4: Alternative - Local Development Setup

If you prefer running without Docker:

### 4.1 Setup Backend

```powershell
# Navigate to backend
cd c:\Stock-Ranking-Website\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Setup local PostgreSQL
# Make sure PostgreSQL is running and create database:
# CREATE DATABASE botleague;

# Update .env with local database URL
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/botleague

# Run database migrations
python -c "from database import init_db; init_db()"

# Start the backend server
python main.py
```

Backend will be available at: http://localhost:8000

### 4.2 Setup Frontend

```powershell
# Open new terminal
cd c:\Stock-Ranking-Website\frontend

# Serve frontend (using Python's built-in server)
python -m http.server 8080
```

Frontend will be available at: http://localhost:8080

### 4.3 Start Background Worker

```powershell
# Open new terminal
cd c:\Stock-Ranking-Website\backend
.\venv\Scripts\Activate.ps1

# Run performance worker
python workers/performance_worker.py
```

## Step 5: Initialize Data

### 5.1 Create Test User

Open browser to http://localhost:8000/docs

Use the interactive API docs:

1. Expand `POST /api/users`
2. Click "Try it out"
3. Enter:
```json
{
  "email": "test@example.com"
}
```
4. Click "Execute"
5. Save the returned `user_id`

### 5.2 Create Test Bot

1. Expand `POST /api/bots`
2. Click "Try it out"
3. Enter:
```json
{
  "user_id": "your-user-id-from-above",
  "name": "Test Bot",
  "strategy_type": "ML",
  "description": "My first trading bot",
  "initial_capital": 100000
}
```
4. Click "Execute"
5. Save the returned `bot_id` and `api_key`

### 5.3 Submit Test Trade Signal

1. Expand `POST /api/signal`
2. Click the lock icon and enter the `api_key` in X-API-Key header
3. Click "Try it out"
4. Enter:
```json
{
  "bot_id": "your-bot-id",
  "ticker": "AAPL",
  "action": "BUY",
  "quantity": 10
}
```
5. Click "Execute"

## Step 6: Verify Everything Works

### 6.1 Check Frontend
Visit http://localhost (or :8080 if local)
- Landing page should load with animations
- Click "Leaderboard" - should show bots

### 6.2 Check API
Visit http://localhost:8000/health
- Should return `{"status": "healthy"}`

### 6.3 Check Database
```powershell
# If using Docker
docker-compose exec db psql -U botleague_user -d botleague

# Run query
SELECT * FROM bots;
```

### 6.4 Check WebSocket
Open browser console on http://localhost
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
```

## Step 7: Development Workflow

### Making Changes

#### Backend Changes
```powershell
# Edit files in backend/
# Changes auto-reload with --reload flag

# View logs
docker-compose logs -f backend
```

#### Frontend Changes
- Edit files in `frontend/`
- Refresh browser to see changes
- No build step required!

### Stopping Services
```powershell
# Stop all containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Restarting Services
```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

## Step 8: Testing Bot Integration

### Create a Simple Bot Script

Create `test_bot.py`:

```python
import requests
import time

API_URL = "http://localhost:8000/api"
BOT_ID = "your-bot-id"
API_KEY = "your-api-key"

def submit_trade(ticker, action, quantity):
    headers = {"X-API-Key": API_KEY}
    data = {
        "bot_id": BOT_ID,
        "ticker": ticker,
        "action": action,
        "quantity": quantity
    }
    
    response = requests.post(
        f"{API_URL}/signal",
        json=data,
        headers=headers
    )
    
    return response.json()

# Test trading
print("Submitting trades...")
print(submit_trade("AAPL", "BUY", 10))
time.sleep(2)
print(submit_trade("GOOGL", "BUY", 5))
time.sleep(2)
print(submit_trade("AAPL", "SELL", 5))

print("\nTrades submitted successfully!")
```

Run it:
```powershell
python test_bot.py
```

## Troubleshooting

### Database Connection Error
```powershell
# Check if PostgreSQL is running
docker-compose ps db

# Check logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Port Already in Use
```powershell
# Find process using port
Get-NetTCPConnection -LocalPort 8000

# Stop Docker containers using port
docker-compose down
```

### Backend Not Starting
```powershell
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for errors
docker-compose logs backend
```

### Frontend Not Loading
```powershell
# Check nginx logs
docker-compose logs frontend

# Verify files exist
Get-ChildItem c:\Stock-Ranking-Website\frontend
```

### WebSocket Connection Failed
- Ensure backend is running
- Check browser console for errors
- Verify WebSocket endpoint: `ws://localhost:8000/ws`

## Next Steps

1. **Explore the UI**
   - Try all frontend pages
   - Test filters and animations
   
2. **Create Multiple Bots**
   - Different strategies
   - Various initial capitals
   
3. **Submit Real Trades**
   - Create a trading algorithm
   - Submit signals via API
   - Watch performance metrics
   
4. **Monitor Performance**
   - Check leaderboards
   - View equity curves
   - Analyze rankings

## Production Deployment

See `README.md` for production deployment guide.

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify configuration in `.env`
3. Ensure all ports are available
4. Check Docker disk space

---

**Happy Trading! 🚀**
