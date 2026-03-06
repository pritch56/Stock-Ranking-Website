"""
Background worker for periodic performance calculations and leaderboard updates.

This worker should be run separately (e.g., via Celery or as a standalone process).
"""

import time
from datetime import datetime
from database import SessionLocal
from services import PerformanceEngine, LeaderboardEngine
from models import Bot

def calculate_all_performance(period: str = "month"):
    """Calculate performance for all active bots"""
    
    db = SessionLocal()
    try:
        performance_engine = PerformanceEngine(db)
        
        # Get all active bots
        bots = db.query(Bot).filter(Bot.is_active == True).all()
        
        print(f"Calculating performance for {len(bots)} bots (period: {period})")
        
        for bot in bots:
            try:
                performance = performance_engine.calculate_performance(bot.id, period)
                print(f"✓ Bot {bot.name}: Return={performance['total_return']:.2%}, Sharpe={performance['sharpe_ratio']:.2f}")
            except Exception as e:
                print(f"✗ Error calculating performance for bot {bot.name}: {e}")
        
        print("Performance calculation complete")
        
    finally:
        db.close()

def update_all_leaderboards():
    """Update leaderboards for all periods"""
    
    db = SessionLocal()
    try:
        leaderboard_engine = LeaderboardEngine(db)
        
        periods = ["week", "month", "year", "5year"]
        
        for period in periods:
            print(f"Updating leaderboard for period: {period}")
            leaderboard_engine.update_rankings(period)
            print(f"✓ Leaderboard updated for {period}")
        
        print("All leaderboards updated")
        
    finally:
        db.close()

def run_periodic_tasks():
    """Run all periodic tasks"""
    
    print(f"[{datetime.now()}] Starting performance calculation and leaderboard update")
    
    # Calculate performance for all periods
    for period in ["week", "month", "year", "5year"]:
        calculate_all_performance(period)
    
    # Update leaderboards
    update_all_leaderboards()
    
    print(f"[{datetime.now()}] Tasks completed")

if __name__ == "__main__":
    print("Starting Performance Worker")
    print("This worker will run every 5 minutes")
    print("Press Ctrl+C to stop")
    
    while True:
        try:
            run_periodic_tasks()
            
            # Sleep for 5 minutes
            print("Sleeping for 5 minutes...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\nStopping worker...")
            break
        except Exception as e:
            print(f"Error in worker: {e}")
            time.sleep(60)  # Sleep 1 minute on error
