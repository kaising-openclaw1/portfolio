"""SQLite-based cache manager"""

import sqlite3
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime

CACHE_DB = "scrape_cache.db"
CACHE_TTL = 3600  # 1 hour default


class CacheManager:
    """SQLite-backed cache for scraped content"""

    def __init__(self, db_path: str = CACHE_DB, ttl: int = CACHE_TTL):
        self.db_path = db_path
        self.ttl = ttl
        self._hits = 0
        self._misses = 0
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                hash TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                format TEXT NOT NULL,
                content TEXT NOT NULL,
                title TEXT,
                timestamp TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON cache(created_at)")
        self.conn.commit()

    def _hash_url(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def get(self, url: str) -> dict | None:
        h = self._hash_url(url)
        row = self.conn.execute(
            "SELECT content, title, timestamp, created_at FROM cache WHERE hash = ?",
            (h,),
        ).fetchone()

        if row and (time.time() - row[3]) < self.ttl:
            self._hits += 1
            return {
                "content": row[0],
                "title": row[1],
                "timestamp": row[2],
            }

        # Expired or not found
        if row:
            self.conn.execute("DELETE FROM cache WHERE hash = ?", (h,))
            self.conn.commit()

        self._misses += 1
        return None

    def save(self, url: str, data: dict):
        h = self._hash_url(url)
        self.conn.execute(
            """INSERT OR REPLACE INTO cache
               (hash, url, format, content, title, timestamp, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                h,
                url,
                data.get("format", "markdown"),
                data["content"],
                data.get("title", ""),
                data.get("timestamp", datetime.now().isoformat()),
                time.time(),
            ),
        )
        self.conn.commit()

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]

    def size(self) -> int:
        p = Path(self.db_path)
        return p.stat().st_size if p.exists() else 0

    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return round(self._hits / total * 100, 1) if total > 0 else 0.0

    def clear_expired(self):
        cutoff = time.time() - self.ttl
        self.conn.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
        self.conn.commit()

    def close(self):
        self.conn.close()
