from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.exam_session import start_quiz_session, is_session_active, clear_quiz_session
from .models import Quiz, QuizAttempt, StudentAnswer, Option


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz(request, quiz_id):
    """Start quiz attempt and register timed session in Redis with TTL [LMS-QZ-02]."""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create new attempt record in PostgreSQL
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz
    )

    # Initialize Redis TTL key
    session_info = start_quiz_session(attempt.id, quiz.id, quiz.time_limit_minutes)

    return Response({
        'attempt_id': str(attempt.id),
        'quiz_title': quiz.title,
        'duration_minutes': quiz.time_limit_minutes,
        'expires_at': session_info.get('expires_at'),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, attempt_id):
    """Submit quiz and calculate grade using ACID transactions [LMS-QZ-03]."""
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id, student=request.user)
    except QuizAttempt.DoesNotExist:
        return Response({'error': 'Quiz attempt not found'}, status=status.HTTP_404_NOT_FOUND)

    if attempt.completed_at is not None:
        return Response({'error': 'Quiz attempt already submitted'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify Redis TTL has not expired
    active, remaining_seconds = is_session_active(attempt_id)
    if not active:
        return Response({'error': 'Exam session has expired. Submission rejected.'}, status=status.HTTP_400_BAD_REQUEST)

    answers_data = request.data.get('answers', [])

    with transaction.atomic():
        correct_count = 0
        total_questions = attempt.quiz.questions.count()

        for ans in answers_data:
            question_id = ans.get('question_id')
            option_id = ans.get('option_id')
            try:
                selected_opt = Option.objects.get(id=option_id, question_id=question_id)
                StudentAnswer.objects.create(
                    attempt=attempt,
                    question_id=question_id,
                    selected_option=selected_opt
                )
                if selected_opt.is_correct:
                    correct_count += 1
            except Option.DoesNotExist:
                continue

        score_percent = int((correct_count / total_questions * 100)) if total_questions > 0 else 0
        is_passed = score_percent >= attempt.quiz.passing_score

        attempt.total_score = score_percent
        attempt.is_passed = is_passed
        attempt.completed_at = timezone.now()
        attempt.save()

    # Clear active session key from Redis
    clear_quiz_session(attempt_id)

    return Response({
        'attempt_id': str(attempt.id),
        'score': score_percent,
        'is_passed': is_passed,
        'correct_answers': correct_count,
        'total_questions': total_questions,
    })
