# app/utils/analytics.py
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

class Analytics:
    """Simple analytics tracker for queries"""
    
    def __init__(self):
        self.query_counter = defaultdict(int)
        self.client_query_counter = defaultdict(lambda: defaultdict(int))
        self.unanswered_counter = defaultdict(lambda: {
            "count": 0,
            "first_seen": None,
            "last_seen": None
        })
    
    def log_query(self, question: str, confidence: str, client_id: str = "unknown"):
        """Log a query for analytics"""
        now = datetime.utcnow().isoformat()
        
        self.query_counter[question] += 1
        self.client_query_counter[client_id][question] += 1
        
        if confidence == "low":
            entry = self.unanswered_counter[question]
            entry["count"] += 1
            entry["first_seen"] = entry["first_seen"] or now
            entry["last_seen"] = now
    
    def get_top_queries(self, limit: int = 10) -> List[Dict]:
        """Get top queries"""
        data = sorted(self.query_counter.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"question": q, "count": c} for q, c in data]
    
    def get_unanswered_questions(self, limit: int = 20) -> List[Dict]:
        """Get unanswered questions"""
        data = sorted(
            self.unanswered_counter.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]
        return [{
            "question": q,
            "count": v["count"],
            "first_seen": v["first_seen"],
            "last_seen": v["last_seen"]
        } for q, v in data]
    
    def get_total_queries(self) -> int:
        """Get total query count"""
        return sum(self.query_counter.values())

# Global analytics instance
analytics = Analytics()
