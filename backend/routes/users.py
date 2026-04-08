from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User

router = APIRouter()

class CreateUserRequest(BaseModel):
    email: str

@router.post("/users")
async def create_user(
    user_request: CreateUserRequest,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user = User(email=user_request.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }

@router.get("/users/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user details"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }

@router.get("/users/{user_id}/bots")
async def get_user_bots(user_id: str, db: Session = Depends(get_db)):
    """Get all bots for a user"""
    
    from models import Bot
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bots = db.query(Bot).filter(Bot.user_id == user_id).all()
    
    return {
        "user_id": user_id,
        "total_bots": len(bots),
        "bots": [
            {
                "bot_id": b.id,
                "name": b.name,
                "strategy_type": b.strategy_type,
                "current_capital": b.current_capital,
                "is_active": b.is_active,
                "api_key": b.api_key,
            }
            for b in bots
        ]
    }
