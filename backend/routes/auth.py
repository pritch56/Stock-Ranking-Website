from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig
from jose import jwt, JWTError
import bcrypt
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from config import settings
from database import get_db
from models import User

router = APIRouter()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


class PasswordAuthRequest(BaseModel):
    email: str
    password: str


# OAuth configuration
oauth_config = StarletteConfig(environ={
    'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
    'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(oauth_config)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


@router.get("/auth/login")
async def login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        email = user_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists, create if not
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email}
        )
        
        # Redirect to frontend; token is delivered via httpOnly cookie only
        response = RedirectResponse(url=f"{settings.FRONTEND_URL}/")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")


@router.post("/auth/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/auth/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current logged-in user"""
    # Try to get token from cookie or Authorization header
    token = request.cookies.get("access_token")
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }


@router.post("/auth/register")
async def register(body: PasswordAuthRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, password_hash=_hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return {"user_id": user.id, "email": user.email}


@router.post("/auth/login/password")
async def login_password(body: PasswordAuthRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.password_hash or not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return {"user_id": user.id, "email": user.email}


@router.get("/auth/check")
async def check_auth(request: Request):
    """Check if user is authenticated"""
    token = request.cookies.get("access_token")
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return {"authenticated": False}
    
    payload = verify_token(token)
    if not payload:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user_id": payload.get("user_id"),
        "email": payload.get("email")
    }
