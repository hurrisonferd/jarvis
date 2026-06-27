"""
Token bucket rate limiter for API calls.
Prevents hitting rate limits by throttling requests.
"""

import time
import threading
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimit:
    """Rate limit configuration."""
    capacity: int  # Max tokens (burst size)
    refill_rate: float  # Tokens per second


class TokenBucket:
    """Thread-safe token bucket implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1, timeout: float = 60.0) -> bool:
        """
        Try to consume tokens. Wait up to timeout seconds.
        Returns True if tokens were consumed, False if timed out.
        """
        deadline = time.time() + timeout
        
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
            
            if time.time() >= deadline:
                return False
            
            # Wait before retrying
            time.sleep(0.1)
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    def available(self) -> float:
        """Get current available tokens."""
        with self.lock:
            self._refill()
            return self.tokens


class MultiLimit:
    """Multiple rate limits (e.g., per-minute, per-hour)."""
    
    def __init__(self, limits: list[RateLimit]):
        self.buckets = [TokenBucket(l.capacity, l.refill_rate) for l in limits]
    
    def consume(self, tokens: int = 1, timeout: float = 60.0) -> bool:
        """Consume one token from each bucket."""
        for bucket in self.buckets:
            if not bucket.consume(tokens, timeout):
                return False
        return True
    
    def wait_for_capacity(self, tokens: int = 1):
        """Block until all buckets have capacity."""
        for bucket in self.buckets:
            while bucket.available() < tokens:
                time.sleep(0.1)


# Common rate limit configurations
RATE_LIMITS = {
    "api_calls_per_minute": MultiLimit([
        RateLimit(capacity=60, refill_rate=1.0)  # 60/min = 1/sec
    ]),
    "api_calls_per_second": MultiLimit([
        RateLimit(capacity=10, refill_rate=10.0)  # 10 burst, 10/sec refill
    ]),
    "git_pushes_per_hour": MultiLimit([
        RateLimit(capacity=50, refill_rate=50/3600)  # 50/hour
    ]),
    "sandboxes_concurrent": MultiLimit([
        RateLimit(capacity=5, refill_rate=0.5)  # 5 concurrent, refill slow
    ]),
}


class RateLimiter:
    """High-level rate limiter with named limits."""
    
    def __init__(self):
        self.limits = RATE_LIMITS.copy()
    
    def can_submit(self, limit_name: str, tokens: int = 1) -> bool:
        """Check if we can consume tokens without blocking."""
        if limit_name not in self.limits:
            return True
        return self.limits[limit_name].buckets[0].available() >= tokens
    
    def consume(self, limit_name: str, tokens: int = 1, timeout: float = 60.0) -> bool:
        """Consume tokens from named limit. Returns False if rate limited."""
        if limit_name not in self.limits:
            return True
        return self.limits[limit_name].consume(tokens, timeout)
    
    def wait_if_needed(self, limit_name: str, tokens: int = 1):
        """Block until we have capacity."""
        if limit_name in self.limits:
            self.limits[limit_name].wait_for_capacity(tokens)


# Global instance
rate_limiter = RateLimiter()