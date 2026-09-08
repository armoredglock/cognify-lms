import time
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def get_session_key(attempt_id):
    """Generate consistent Redis key for active quiz session."""
    return f"quiz_session:{attempt_id}"

def start_quiz_session(attempt_id, quiz_id, duration_minutes):
    """Create Redis session key with TTL (exam duration + 2 min buffer) [LMS-QZ-02]."""
    key = get_session_key(attempt_id)
    ttl_seconds = (duration_minutes * 60) + 120  # 2 minute buffer for network latency
    session_data = {
        'quiz_id': str(quiz_id),
        'started_at': int(time.time()),
        'expires_at': int(time.time()) + (duration_minutes * 60),
    }
    try:
        cache.set(key, session_data, timeout=ttl_seconds)
        return session_data
    except Exception as e:
        logger.warning(f"Failed to set quiz session in Redis: {e}")
        return session_data

def is_session_active(attempt_id):
    """Verify whether the quiz session has expired in Redis."""
    key = get_session_key(attempt_id)
    try:
        session = cache.get(key)
        if not session:
            # TTL expired
            return False, 0
        remaining_seconds = max(0, session['expires_at'] - int(time.time()))
        return True, remaining_seconds
    except Exception as e:
        logger.warning(f"Redis session lookup error: {e}")
        return True, 0

def clear_quiz_session(attempt_id):
    """Remove session from Redis upon submission."""
    key = get_session_key(attempt_id)
    try:
        cache.delete(key)
    except Exception:
        pass
