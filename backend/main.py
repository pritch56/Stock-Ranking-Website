from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import json

from config import settings
from database import init_db, get_db
from routes import signals, bots, leaderboard, users
from services import LeaderboardEngine

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Trading Bot League API...")
    init_db()
    print("✅ Database initialized")
    
    # Initialize default leagues
    from database import SessionLocal
    from services import LeaderboardEngine
    db = SessionLocal()
    try:
        leaderboard_engine = LeaderboardEngine(db)
        leaderboard_engine.initialize_leagues()
        print("✅ Leagues initialized")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Trading bot competition platform with real-time rankings",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signals.router, prefix=f"{settings.API_V1_STR}", tags=["signals"])
app.include_router(bots.router, prefix=f"{settings.API_V1_STR}", tags=["bots"])
app.include_router(leaderboard.router, prefix=f"{settings.API_V1_STR}", tags=["leaderboard"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}", tags=["users"])

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Trading Bot League API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Clients can connect to receive:
    - Live trade notifications
    - Leaderboard rank changes
    - Performance updates
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to Trading Bot League WebSocket"
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            
            # Echo back for now (in production, handle different message types)
            await websocket.send_json({
                "type": "echo",
                "data": data
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from WebSocket")

async def broadcast_trade_update(trade_data: dict):
    """Broadcast trade update to all connected clients"""
    await manager.broadcast({
        "type": "trade",
        "data": trade_data
    })

async def broadcast_leaderboard_update(leaderboard_data: dict):
    """Broadcast leaderboard update to all connected clients"""
    await manager.broadcast({
        "type": "leaderboard",
        "data": leaderboard_data
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
