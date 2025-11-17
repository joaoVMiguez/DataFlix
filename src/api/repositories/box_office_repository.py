"""
Box Office data repository
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BoxOfficeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_stats(self) -> Dict[str, Any]:
        """Get box office statistics"""
        query = text("""
            SELECT 
                COALESCE(SUM(revenue), 0) as total_revenue,
                COALESCE(SUM(profit), 0) as total_profit,
                COALESCE(AVG(roi), 0) as avg_roi,
                COUNT(*) FILTER (WHERE is_blockbuster = true) as blockbusters_count
            FROM gold_tmdb.fact_box_office
        """)
        result = self.db.execute(query).fetchone()
        
        total_revenue = result.total_revenue or 0
        total_profit = result.total_profit or 0
        avg_roi = result.avg_roi or 0
        
        return {
            "total_revenue": f"US$ {total_revenue / 1_000_000_000:.1f} bi",
            "total_profit": f"US$ {total_profit / 1_000_000_000:.1f} bi",
            "avg_roi": f"{avg_roi * 100:.0f}%",
            "blockbusters_count": result.blockbusters_count or 0
        }
    
    def get_top_profitable_movies(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most profitable movies"""
        query = text("""
            SELECT 
                movielens_id,
                title,
                release_year,
                budget,
                revenue,
                profit,
                COALESCE(roi, 0) as roi,
                COALESCE(payback_ratio, 0) as payback_ratio,
                budget_category,
                revenue_category,
                roi_category,
                is_blockbuster,
                is_profitable
            FROM gold_tmdb.fact_box_office
            WHERE is_profitable = true
            ORDER BY roi DESC, profit DESC
            LIMIT :limit
        """)
        results = self.db.execute(query, {"limit": limit}).fetchall()
        
        return [
            {
                "movielens_id": r.movielens_id,
                "title": r.title,
                "release_year": r.release_year,
                "budget": r.budget,
                "revenue": r.revenue,
                "profit": r.profit,
                "roi": float(r.roi) if r.roi is not None else 0.0,
                "payback_ratio": float(r.payback_ratio) if r.payback_ratio is not None else 0.0,
                "budget_category": r.budget_category or "Unknown",
                "revenue_category": r.revenue_category or "Unknown",
                "roi_category": r.roi_category or "Unknown",
                "is_blockbuster": r.is_blockbuster,
                "is_profitable": r.is_profitable
            }
            for r in results
        ]
    
    def get_performance_indicators(self) -> Dict[str, Any]:
        """Get performance indicators"""
        query = text("""
            SELECT 
                (COUNT(*) FILTER (WHERE is_profitable = true)::float / NULLIF(COUNT(*)::float, 0) * 100) as profitability_rate,
                AVG(CASE WHEN is_blockbuster = true THEN 1 ELSE 0 END) * 5 as avg_blockbusters
            FROM gold_tmdb.fact_box_office
        """)
        result = self.db.execute(query).fetchone()
        
        return {
            "profitability_rate": float(result.profitability_rate or 0),
            "avg_blockbusters": float(result.avg_blockbusters or 0)
        }
    
    def get_highest_profit(self) -> Dict[str, Any]:
        """Get movie with highest profit"""
        query = text("""
            SELECT title, profit
            FROM gold_tmdb.fact_box_office
            ORDER BY profit DESC
            LIMIT 1
        """)
        result = self.db.execute(query).fetchone()
        
        if result:
            return {
                "highest_profit_movie": result.title,
                "highest_profit_value": int(result.profit)
            }
        return {
            "highest_profit_movie": "N/A",
            "highest_profit_value": 0
        }