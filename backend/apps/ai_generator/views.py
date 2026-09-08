from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AIAssessmentArtifact
from .services import generate_assessment_from_transcript
from apps.courses.models import Lesson


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_lesson_ai_materials(request, lesson_id):
    """Generate and store AI quiz/flashcards for a lesson transcript [LMS-AI-02]."""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

    generated_data = generate_assessment_from_transcript(lesson.transcript, topic=lesson.title)

    # Save to PostgreSQL
    artifact = AIAssessmentArtifact.objects.create(
        lesson=lesson,
        artifact_type=AIAssessmentArtifact.ArtifactType.QUIZ,
        content=generated_data
    )

    return Response({
        'artifact_id': str(artifact.id),
        'lesson_id': str(lesson.id),
        'generated_materials': generated_data,
    }, status=status.HTTP_201_CREATED)
