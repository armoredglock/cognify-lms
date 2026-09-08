from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.redis_cache import update_playback_heartbeat, get_cached_playback
from .models import LessonProgress
from apps.courses.models import Lesson


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def playback_heartbeat(request):
    """Receive client video playback heartbeat and cache into Redis [LMS-VID-02]."""
    lesson_id = request.data.get('lesson_id')
    second = request.data.get('second', 0)

    if not lesson_id:
        return Response({'error': 'lesson_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Update fast in-memory Redis cache
    cached = update_playback_heartbeat(request.user.id, lesson_id, second)

    return Response({
        'status': 'heartbeat_recorded',
        'lesson_id': lesson_id,
        'second': second,
        'cached_in_redis': cached,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_lesson_progress(request, lesson_id):
    """Durable sync from Redis to PostgreSQL LessonProgress [LMS-VID-03]."""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

    cached_data = get_cached_playback(request.user.id, lesson_id)
    last_second = cached_data.get('last_second', 0) if cached_data else 0

    # Mark completed if reached 90% or explicitly passed
    is_completed = False
    if lesson.duration_seconds > 0 and last_second >= (lesson.duration_seconds * 0.9):
        is_completed = True

    progress, created = LessonProgress.objects.update_or_create(
        student=request.user,
        lesson=lesson,
        defaults={
            'last_watched_second': last_second,
            'is_completed': is_completed,
        }
    )

    return Response({
        'synced': True,
        'last_watched_second': progress.last_watched_second,
        'is_completed': progress.is_completed,
    })
