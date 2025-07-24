# In-memory data model for URL shortener
import threading
import time

class URLStore:
    """
    Thread-safe in-memory store for URL mappings, click counts, and creation timestamps.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}  # short_code -> { 'url': ..., 'created_at': ..., 'clicks': ... }

    def add_url(self, short_code, url):
        with self.lock:
            self.data[short_code] = {
                'url': url,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'clicks': 0
            }

    def get_url(self, short_code):
        with self.lock:
            return self.data.get(short_code)

    def increment_click(self, short_code):
        """
        Increment the click count for a short_code. Thread-safe.
        Returns True if successful, False if code not found.
        """
        with self.lock:
            if short_code in self.data:
                self.data[short_code]['clicks'] += 1
                return True
            return False

    def get_stats(self, short_code):
        """
        Return stats (url, clicks, created_at) for a short_code, or None if not found. Thread-safe.
        """
        with self.lock:
            entry = self.data.get(short_code)
            if entry:
                return {
                    'url': entry['url'],
                    'clicks': entry['clicks'],
                    'created_at': entry['created_at']
                }
            return None

# Singleton instance
url_store = URLStore()