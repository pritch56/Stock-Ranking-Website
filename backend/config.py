from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/botleague"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Trading Bot League"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Trading
    INITIAL_CAPITAL: float = 100000.0
    MAX_POSITION_SIZE: float = 1.0  # 100% of capital max
    SLIPPAGE_BPS: float = 5.0  # 5 basis points
    
    # Market Data
    MARKET_DATA_PROVIDER: str = "polygon"  # or 'alpaca', 'yahoo'
    POLYGON_API_KEY: Optional[str] = None
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
