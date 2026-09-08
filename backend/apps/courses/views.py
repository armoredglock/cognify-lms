from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Course, Enrollment


@api_view(['GET'])
@permission_classes([AllowAny])
def list_courses(request):
    """List published courses [LMS-CRS-03]."""
    courses = Course.objects.filter(is_published=True).values(
        'id', 'title', 'slug', 'description', 'category', 'instructor__username', 'created_at'
    )
    return Response(list(courses))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
    """Enroll currently authenticated student in course [LMS-CRS-03]."""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    return Response({
        'enrolled': True,
        'created': created,
        'course_title': course.title,
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
