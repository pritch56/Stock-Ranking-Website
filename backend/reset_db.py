"""Drop and recreate all database tables."""
from database import engine, Base
from models import user, bot, league, performance, ranking, signal, trade
from sqlalchemy import text

if __name__ == "__main__":
    print("Dropping all tables with CASCADE...")
    with engine.connect() as conn:
        # Drop all tables that might exist
        tables = ['trades', 'signals', 'rankings', 'performance', 'bots', 'leagues', 'users']
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"Dropped {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        conn.commit()
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")
