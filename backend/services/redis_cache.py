import time
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def get_video_cache_key(user_id, lesson_id):
    """Generate consistent Redis key for active playback state."""
    return f"video:user:{user_id}:lesson:{lesson_id}"

def update_playback_heartbeat(user_id, lesson_id, second):
    """Store high-frequency video playback tick in Redis with 24h TTL [LMS-VID-01]."""
    key = get_video_cache_key(user_id, lesson_id)
    payload = {
        'last_second': int(second),
        'updated_at': int(time.time()),
    }
    try:
        cache.set(key, payload, timeout=86400)
        return True
    except Exception as e:
        logger.warning(f"Failed to cache playback heartbeat in Redis: {e}")
        return False

def get_cached_playback(user_id, lesson_id):
    """Retrieve last cached playback timestamp from Redis."""
    key = get_video_cache_key(user_id, lesson_id)
    try:
        return cache.get(key)
    except Exception as e:
        logger.warning(f"Failed to fetch playback heartbeat from Redis: {e}")
        return None
