# app/utils/analytics.py
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
import json
import os

class Analytics:
    """Persistent analytics tracker for queries"""
    
    def __init__(self, storage_file: str = "analytics_data.json"):
        self.storage_file = storage_file
        self.query_counter = defaultdict(int)
        self.client_query_counter = defaultdict(lambda: defaultdict(int))
        self.unanswered_counter = defaultdict(lambda: {
            "count": 0,
            "first_seen": None,
            "last_seen": None
        })
        self.feedback_data = []  # List of feedback entries
        self._load_from_storage()
    
    def _load_from_storage(self):
        """Load analytics from persistent storage"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load query counter
                    self.query_counter = defaultdict(int, data.get("query_counter", {}))
                    
                    # Load client query counter
                    client_data = data.get("client_query_counter", {})
                    for client_id, queries in client_data.items():
                        self.client_query_counter[client_id] = defaultdict(int, queries)
                    
                    # Load unanswered counter
                    unanswered_data = data.get("unanswered_counter", {})
                    for question, info in unanswered_data.items():
                        self.unanswered_counter[question] = info
                    
                    # Load feedback data
                    self.feedback_data = data.get("feedback_data", [])
                    
                    print(f"✓ Loaded analytics from {self.storage_file}")
                    print(f"  - Total feedback entries: {len(self.feedback_data)}")
        except Exception as e:
            print(f"⚠ Could not load analytics: {e}")
    
    def _save_to_storage(self):
        """Save analytics to persistent storage"""
        try:
            data = {
                "query_counter": dict(self.query_counter),
                "client_query_counter": {
                    client_id: dict(queries)
                    for client_id, queries in self.client_query_counter.items()
                },
                "unanswered_counter": dict(self.unanswered_counter),
                "feedback_data": self.feedback_data,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Could not save analytics: {e}")
    
    def log_query(self, question: str, confidence: str, client_id: str = "unknown"):
        """Log a query for analytics and save to storage"""
        now = datetime.utcnow().isoformat()
        
        self.query_counter[question] += 1
        self.client_query_counter[client_id][question] += 1
        
        if confidence == "low":
            entry = self.unanswered_counter[question]
            entry["count"] += 1
            entry["first_seen"] = entry["first_seen"] or now
            entry["last_seen"] = now
        
        # Save to persistent storage after each log
        self._save_to_storage()
    
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
    
    def log_feedback(self, feedback_entry: Dict):
        """Log user feedback and save to storage"""
        self.feedback_data.append(feedback_entry)
        self._save_to_storage()
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        if not self.feedback_data:
            return {
                "total_feedback": 0,
                "positive": 0,
                "negative": 0,
                "positive_rate": 0.0,
                "recent_feedback": []
            }
        
        positive = sum(1 for f in self.feedback_data if f.get("feedback") == "positive")
        negative = sum(1 for f in self.feedback_data if f.get("feedback") == "negative")
        total = len(self.feedback_data)
        
        # Get recent feedback (last 20)
        recent = sorted(
            self.feedback_data,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:20]
        
        return {
            "total_feedback": total,
            "positive": positive,
            "negative": negative,
            "positive_rate": round((positive / total * 100), 2) if total > 0 else 0.0,
            "recent_feedback": recent
        }
    
    def get_negative_feedback(self, limit: int = 20) -> List[Dict]:
        """Get recent negative feedback for improvement"""
        negative = [f for f in self.feedback_data if f.get("feedback") == "negative"]
        return sorted(
            negative,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:limit]

# Global analytics instance with persistent storage
analytics = Analytics()
