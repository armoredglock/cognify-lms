import logging
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

def get_leaderboard_key(course_id):
    """Generate consistent Redis key for Course Leaderboard Sorted Set."""
    return f"leaderboard:course:{course_id}"

def update_user_score(course_id, username, score_delta):
    """Increment user points in Redis Sorted Set [LMS-GAM-01]."""
    key = get_leaderboard_key(course_id)
    try:
        con = get_redis_connection("default")
        con.zincrby(key, score_delta, username)
        return True
    except Exception as e:
        logger.warning(f"Redis leaderboard update error: {e}")
        return False

def get_top_rankers(course_id, limit=10):
    """Retrieve top N ranked students from Redis Sorted Set [LMS-GAM-02]."""
    key = get_leaderboard_key(course_id)
    try:
        con = get_redis_connection("default")
        # ZREVRANGE with scores descending
        results = con.zrevrange(key, 0, limit - 1, withscores=True)
        leaderboard = []
        for rank, (user_bytes, score) in enumerate(results, start=1):
            leaderboard.append({
                'rank': rank,
                'username': user_bytes.decode('utf-8') if isinstance(user_bytes, bytes) else str(user_bytes),
                'score': int(score),
            })
        return leaderboard
    except Exception as e:
        logger.warning(f"Redis leaderboard fetch error: {e}")
        return []
