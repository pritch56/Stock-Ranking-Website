"""Test script to verify all API endpoints and database connections"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health check: {response.json()}")
    return response.status_code == 200

def test_create_user():
    """Test user creation"""
    data = {"email": f"test_{datetime.now().timestamp()}@example.com"}
    response = requests.post(f"{API_URL}/users", json=data)
    if response.status_code == 200:
        user = response.json()
        print(f"✓ Created user: {user['user_id']}")
        return user['user_id']
    else:
        print(f"✗ Failed to create user: {response.text}")
        return None

def test_create_bot(user_id):
    """Test bot creation"""
    data = {
        "user_id": user_id,
        "name": "Test Bot",
        "strategy_type": "ML",
        "description": "Test trading bot",
        "initial_capital": 100000.0
    }
    response = requests.post(f"{API_URL}/bots", json=data)
    if response.status_code == 200:
        bot = response.json()
        print(f"✓ Created bot: {bot['bot_id']}")
        print(f"  API Key: {bot['api_key']}")
        return bot
    else:
        print(f"✗ Failed to create bot: {response.text}")
        return None

def test_submit_signal(api_key):
    """Test signal submission"""
    data = {
        "ticker": "AAPL",
        "action": "BUY",
        "quantity": 10
    }
    headers = {"X-API-Key": api_key}
    response = requests.post(f"{API_URL}/signal", json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Submitted signal: {result.get('message')}")
        return True
    else:
        print(f"✗ Failed to submit signal: {response.text}")
        return False

def test_leaderboard():
    """Test leaderboard endpoint"""
    response = requests.get(f"{API_URL}/leaderboard?period=month&limit=10")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Leaderboard loaded: {data['total_bots']} bots")
        return True
    else:
        print(f"✗ Failed to load leaderboard: {response.text}")
        return False

def test_live_trades():
    """Test live trades endpoint"""
    response = requests.get(f"{API_URL}/trades/live?limit=10")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Live trades loaded: {len(data['trades'])} trades")
        return True
    else:
        print(f"✗ Failed to load live trades: {response.text}")
        return False

def test_leagues():
    """Test leagues endpoint"""
    response = requests.get(f"{API_URL}/leagues")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Leagues loaded: {data['total']} leagues")
        return True
    else:
        print(f"✗ Failed to load leagues: {response.text}")
        return False

def test_frontend_pages():
    """Test that frontend pages are accessible"""
    pages = ["/", "/dashboard.html", "/leaderboard.html", "/bot.html"]
    for page in pages:
        response = requests.get(f"{BASE_URL}{page}")
        if response.status_code == 200:
            print(f"✓ Page accessible: {page}")
        else:
            print(f"✗ Page not accessible: {page}")

def test_static_files():
    """Test that static files are accessible"""
    files = [
        "/css/styles.css",
        "/js/main.js",
        "/js/dashboard.js",
        "/js/leaderboard.js",
        "/js/bot.js",
        "/js/particles-config.js"
    ]
    for file in files:
        response = requests.get(f"{BASE_URL}{file}")
        if response.status_code == 200:
            print(f"✓ Static file accessible: {file}")
        else:
            print(f"✗ Static file not accessible: {file}")

if __name__ == "__main__":
    print("=" * 60)
    print("TRADING BOT LEAGUE - CONNECTION TEST")
    print("=" * 60)
    
    print("\n1. Testing Backend API...")
    print("-" * 60)
    test_health()
    user_id = test_create_user()
    
    if user_id:
        bot = test_create_bot(user_id)
        if bot:
            test_submit_signal(bot['api_key'])
            test_submit_signal(bot['api_key'])  # Submit a second trade
    
    test_leaderboard()
    test_live_trades()
    test_leagues()
    
    print("\n2. Testing Frontend Pages...")
    print("-" * 60)
    test_frontend_pages()
    
    print("\n3. Testing Static Files...")
    print("-" * 60)
    test_static_files()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nServer is running at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
