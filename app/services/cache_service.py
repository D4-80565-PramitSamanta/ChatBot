# app/services/cache_service.py
import json
import hashlib
import time
from typing import Dict, Any, Optional
from pathlib import Path

class CacheService:
    """Hybrid caching service for responses and documentation"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache settings
        self.response_cache_ttl = 3600  # 1 hour for responses
        self.doc_cache_ttl = 1800       # 30 minutes for documentation
        
        # Cache files
        self.response_cache_file = self.cache_dir / "responses.json"
        self.doc_cache_file = self.cache_dir / "documentation.json"
        
        # Load existing caches
        self.response_cache = self._load_cache(self.response_cache_file)
        self.doc_cache = self._load_cache(self.doc_cache_file)
        
        print("✓ Cache Service initialized - Hybrid mode enabled")
    
    def _load_cache(self, cache_file: Path) -> Dict[str, Any]:
        """Load cache from file"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache {cache_file}: {e}")
        return {}
    
    def _save_cache(self, cache_data: Dict[str, Any], cache_file: Path):
        """Save cache to file"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save cache {cache_file}: {e}")
    
    def _generate_key(self, content: str) -> str:
        """Generate cache key from content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > ttl
    
    def get_response(self, question: str, input_type: str = "question") -> Optional[Dict[str, Any]]:
        """Get cached response"""
        cache_key = self._generate_key(f"{input_type}:{question}")
        
        if cache_key in self.response_cache:
            entry = self.response_cache[cache_key]
            if not self._is_expired(entry['timestamp'], self.response_cache_ttl):
                print(f"🚀 Cache HIT - Response found for: {question[:50]}...")
                return entry['data']
            else:
                # Remove expired entry
                del self.response_cache[cache_key]
                print(f"⏰ Cache EXPIRED - Removing old response")
        
        print(f"❌ Cache MISS - No cached response found")
        return None
    
    def set_response(self, question: str, response_data: Dict[str, Any], input_type: str = "question"):
        """Cache response"""
        cache_key = self._generate_key(f"{input_type}:{question}")
        
        self.response_cache[cache_key] = {
            'timestamp': time.time(),
            'question': question,
            'input_type': input_type,
            'data': response_data
        }
        
        self._save_cache(self.response_cache, self.response_cache_file)
        print(f"💾 Cached response for: {question[:50]}...")
    
    def get_documentation(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached documentation"""
        cache_key = self._generate_key(query)
        
        if cache_key in self.doc_cache:
            entry = self.doc_cache[cache_key]
            if not self._is_expired(entry['timestamp'], self.doc_cache_ttl):
                print(f"📚 Doc Cache HIT - Documentation found for: {query[:50]}...")
                return entry['data']
            else:
                # Remove expired entry
                del self.doc_cache[cache_key]
                print(f"⏰ Doc Cache EXPIRED - Removing old documentation")
        
        print(f"📚 Doc Cache MISS - No cached documentation found")
        return None
    
    def set_documentation(self, query: str, doc_data: Dict[str, Any]):
        """Cache documentation"""
        cache_key = self._generate_key(query)
        
        self.doc_cache[cache_key] = {
            'timestamp': time.time(),
            'query': query,
            'data': doc_data
        }
        
        self._save_cache(self.doc_cache, self.doc_cache_file)
        print(f"📚 Cached documentation for: {query[:50]}...")
    
    def clear_cache(self, cache_type: str = "all"):
        """Clear cache"""
        if cache_type in ["all", "responses"]:
            self.response_cache.clear()
            self._save_cache(self.response_cache, self.response_cache_file)
            print("🗑️ Response cache cleared")
        
        if cache_type in ["all", "documentation"]:
            self.doc_cache.clear()
            self._save_cache(self.doc_cache, self.doc_cache_file)
            print("🗑️ Documentation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        
        # Count valid (non-expired) entries
        valid_responses = sum(1 for entry in self.response_cache.values() 
                            if not self._is_expired(entry['timestamp'], self.response_cache_ttl))
        
        valid_docs = sum(1 for entry in self.doc_cache.values() 
                        if not self._is_expired(entry['timestamp'], self.doc_cache_ttl))
        
        return {
            "response_cache": {
                "total_entries": len(self.response_cache),
                "valid_entries": valid_responses,
                "ttl_seconds": self.response_cache_ttl
            },
            "doc_cache": {
                "total_entries": len(self.doc_cache),
                "valid_entries": valid_docs,
                "ttl_seconds": self.doc_cache_ttl
            }
        }