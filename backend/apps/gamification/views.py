import hashlib
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from services.leaderboard import get_top_rankers
from .models import Certificate
from apps.courses.models import Course


@api_view(['GET'])
@permission_classes([AllowAny])
def course_leaderboard(request, course_id):
    """Fetch top leaderboard ranks from Redis Sorted Set [LMS-GAM-02]."""
    limit = int(request.query_params.get('limit', 10))
    leaders = get_top_rankers(course_id, limit=limit)
    return Response({'course_id': str(course_id), 'leaderboard': leaders})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_certificate(request, course_id):
    """Generate verified certificate with SHA-256 hash [LMS-GAM-03]."""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    raw_string = f"{request.user.id}:{course.id}:{uuid.uuid4()}"
    verification_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    certificate, created = Certificate.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'verification_hash': verification_hash}
    )

    return Response({
        'certificate_id': str(certificate.id),
        'student': request.user.username,
        'course': course.title,
        'verification_hash': certificate.verification_hash,
        'issued_at': certificate.issued_at,
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
