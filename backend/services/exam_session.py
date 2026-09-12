import time
import logging
from typing import Tuple, Optional, Dict, Any
from django.core.cache import cache

logger = logging.getLogger(__name__)

# 2 minute buffer for network latency and client-server clock skew
GRACE_PERIOD_SECONDS = 120


def get_session_key(attempt_id: Any) -> str:
    """Generate consistent Redis key for active quiz session [LMS-QZ-02]."""
    return f"quiz_session:{attempt_id}"


def start_quiz_session(
    attempt_id: Any,
    quiz_id: Any,
    duration_minutes: int,
    student_id: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Create Redis session key with TTL (exam duration + 2 min buffer) [LMS-QZ-02].

    Key Pattern: quiz_session:{attempt_id}
    TTL: duration_minutes * 60 + 120 seconds
    """
    key = get_session_key(attempt_id)
    ttl_seconds = (duration_minutes * 60) + GRACE_PERIOD_SECONDS
    now = int(time.time())
    expires_at = now + (duration_minutes * 60)

    session_data = {
        'attempt_id': str(attempt_id),
        'quiz_id': str(quiz_id),
        'student_id': str(student_id) if student_id else None,
        'started_at': now,
        'expires_at': expires_at,
        'duration_minutes': duration_minutes,
        'grace_buffer_seconds': GRACE_PERIOD_SECONDS,
    }

    try:
        cache.set(key, session_data, timeout=ttl_seconds)
        return session_data
    except Exception as e:
        logger.warning(f"Failed to set quiz session in Redis: {e}")
        return session_data


def is_session_active(attempt_id: Any) -> Tuple[bool, int]:
    """
    Verify whether the quiz session has expired in Redis [LMS-QZ-02].

    Returns:
        (is_active: bool, remaining_seconds: int)
    """
    key = get_session_key(attempt_id)
    try:
        session = cache.get(key)
        if not session:
            # TTL expired in Redis
            return False, 0

        now = int(time.time())
        expires_at = session.get('expires_at', 0)
        grace_deadline = expires_at + GRACE_PERIOD_SECONDS

        if now > grace_deadline:
            # Past official time plus grace period
            return False, 0

        remaining_seconds = max(0, expires_at - now)
        return True, remaining_seconds
    except Exception as e:
        logger.warning(f"Redis session lookup error: {e}")
        return True, 0


def get_session_data(attempt_id: Any) -> Optional[Dict[str, Any]]:
    """Retrieve full active session payload from Redis [LMS-QZ-02]."""
    key = get_session_key(attempt_id)
    try:
        return cache.get(key)
    except Exception as e:
        logger.warning(f"Error fetching quiz session data: {e}")
        return None


def get_remaining_seconds(attempt_id: Any) -> int:
    """Convenience helper returning remaining seconds until quiz expires."""
    active, remaining = is_session_active(attempt_id)
    return remaining if active else 0


def clear_quiz_session(attempt_id: Any) -> bool:
    """Remove session from Redis upon submission [LMS-QZ-02]."""
    key = get_session_key(attempt_id)
    try:
        cache.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Error clearing quiz session: {e}")
        return False
