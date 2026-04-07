from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models import Bot, Performance, League, Ranking
from typing import List, Dict

class LeaderboardEngine:
    """Manages leaderboards and rankings"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_leaderboard(self, period: str = "month", league: str = "global", limit: int = 100) -> List[Dict]:
        """Get leaderboard for a specific period and league"""
        
        # Build query
        query = self.db.query(
            Bot.id,
            Bot.name,
            Bot.strategy_type,
            Performance.total_return,
            Performance.sharpe_ratio,
            Performance.max_drawdown,
            Performance.win_rate,
            Performance.total_trades
        ).join(
            Performance,
            and_(
                Bot.id == Performance.bot_id,
                Performance.period == period
            )
        )
        
        # Filter by league/strategy if not global
        if league != "global":
            query = query.filter(Bot.strategy_type == league)
        
        # Order by risk-adjusted score (Sharpe ratio * return)
        results = query.all()
        
        # Calculate scores and rank
        leaderboard = []
        for bot in results:
            score = self.calculate_score(bot.total_return, bot.sharpe_ratio)
            leaderboard.append({
                "bot_id": bot.id,
                "bot_name": bot.name,
                "strategy": bot.strategy_type,
                "return": bot.total_return,
                "sharpe_ratio": bot.sharpe_ratio,
                "max_drawdown": bot.max_drawdown,
                "win_rate": bot.win_rate,
                "total_trades": bot.total_trades,
                "score": score
            })
        
        # Sort by score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return leaderboard[:limit]
    
    def calculate_score(self, return_pct: float, sharpe_ratio: float) -> float:
        """Calculate risk-adjusted score for ranking"""
        
        # Weighted combination of return and Sharpe ratio
        # Higher Sharpe ratio means better risk-adjusted returns
        
        if sharpe_ratio <= 0:
            # Penalize negative Sharpe
            score = return_pct * 0.5
        else:
            # Reward positive risk-adjusted returns
            score = return_pct * 0.6 + (sharpe_ratio / 10.0) * 0.4
        
        return round(score, 6)
    
    def update_rankings(self, period: str):
        """Update all league rankings for a period"""
        
        # Get all leagues
        leagues = self.db.query(League).all()
        
        for league in leagues:
            # Get leaderboard for this league
            leaderboard = self.get_leaderboard(
                period=period,
                league=league.strategy_type if league.strategy_type != "Global" else "global"
            )
            
            # Update rankings
            for entry in leaderboard:
                ranking_id = f"{league.id}:{entry['bot_id']}:{period}"
                ranking = self.db.query(Ranking).filter(Ranking.id == ranking_id).first()
                
                if not ranking:
                    ranking = Ranking(
                        id=ranking_id,
                        league_id=league.id,
                        bot_id=entry['bot_id'],
                        period=period
                    )
                
                # Track rank changes
                ranking.previous_rank = ranking.rank if ranking.rank else None
                ranking.rank = entry['rank']
                ranking.score = entry['score']
                
                self.db.merge(ranking)
            
            self.db.commit()
    
    def get_bot_ranking(self, bot_id: str, period: str = "month") -> Dict:
        """Get ranking information for a specific bot"""

        results = self.db.query(Ranking, League).join(
            League, League.id == Ranking.league_id
        ).filter(
            and_(
                Ranking.bot_id == bot_id,
                Ranking.period == period
            )
        ).all()

        return {
            "bot_id": bot_id,
            "period": period,
            "rankings": [
                {
                    "league": league.name,
                    "rank": ranking.rank,
                    "previous_rank": ranking.previous_rank,
                    "score": ranking.score
                }
                for ranking, league in results
            ]
        }
    
    def get_top_performers(self, limit: int = 10) -> List[Dict]:
        """Get top performing bots across all time"""

        results = self.db.query(Bot, Performance).join(
            Performance,
            and_(Bot.id == Performance.bot_id, Performance.period == "year")
        ).order_by(
            desc(Performance.total_return)
        ).limit(limit).all()

        return [
            {
                "bot_id": bot.id,
                "bot_name": bot.name,
                "strategy": bot.strategy_type,
                "return": perf.total_return,
                "sharpe_ratio": perf.sharpe_ratio
            }
            for bot, perf in results
        ]
    
    def initialize_leagues(self):
        """Initialize default leagues"""
        
        default_leagues = [
            {"name": "Global League", "strategy_type": "Global", "description": "All bots compete"},
            {"name": "Machine Learning", "strategy_type": "ML", "description": "ML-based trading bots"},
            {"name": "High Frequency", "strategy_type": "HFT", "description": "High frequency trading bots"},
            {"name": "Sentiment Analysis", "strategy_type": "Sentiment", "description": "Sentiment-based strategies"},
            {"name": "Technical Analysis", "strategy_type": "Technical", "description": "Technical analysis bots"},
            {"name": "Arbitrage", "strategy_type": "Arbitrage", "description": "Arbitrage strategies"},
        ]
        
        for league_data in default_leagues:
            existing = self.db.query(League).filter(League.name == league_data["name"]).first()
            if not existing:
                league = League(**league_data)
                self.db.add(league)
        
        self.db.commit()
