from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from config import settings
from database import init_db
from routes import signals, bots, leaderboard, users, auth
from ws_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    from database import SessionLocal
    from services import LeaderboardEngine
    from seed_data import run as seed
    db = SessionLocal()
    try:
        LeaderboardEngine(db).initialize_leagues()
    finally:
        db.close()

    seed()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Trading bot competition platform with real-time rankings",
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
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
app.include_router(auth.router, tags=["auth"])


@app.get("/api")
async def api_root():
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


# Serve frontend HTML pages
frontend_path = Path(__file__).parent.parent / "frontend"

@app.get("/dashboard.html")
async def serve_dashboard():
    return FileResponse(str(frontend_path / "dashboard.html"))


@app.get("/leaderboard.html")
async def serve_leaderboard():
    return FileResponse(str(frontend_path / "leaderboard.html"))


@app.get("/bot.html")
async def serve_bot():
    return FileResponse(str(frontend_path / "bot.html"))


# Mount static files (CSS, JS) - must be after specific routes
app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")


# Root must be last to not interfere with other routes
@app.get("/")
async def serve_index():
    return FileResponse(str(frontend_path / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
