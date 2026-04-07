from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routes import signals, bots, leaderboard, users
from ws_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    from database import SessionLocal
    from services import LeaderboardEngine
    db = SessionLocal()
    try:
        LeaderboardEngine(db).initialize_leagues()
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Trading bot competition platform with real-time rankings",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals.router, prefix=settings.API_V1_STR, tags=["signals"])
app.include_router(bots.router, prefix=settings.API_V1_STR, tags=["bots"])
app.include_router(leaderboard.router, prefix=settings.API_V1_STR, tags=["leaderboard"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])


@app.get("/")
async def root():
    return {"message": "Trading Bot League API", "version": "1.0.0", "docs": "/docs", "status": "operational"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "connection", "message": "Connected to Trading Bot League"})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
