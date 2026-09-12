from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.exam_session import (
    start_quiz_session,
    is_session_active,
    clear_quiz_session,
)
from .models import Quiz, QuizAttempt, StudentAnswer, Option


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz(request, quiz_id):
    """
    Start quiz attempt and register timed session in Redis with TTL [LMS-QZ-02].

    If the student already has an active, unsubmitted attempt with an unexpired timer,
    the active session is resumed to avoid duplicate orphan attempts.
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check for an ongoing unsubmitted attempt
    existing_attempt = QuizAttempt.objects.filter(
        student=request.user,
        quiz=quiz,
        completed_at__isnull=True
    ).order_by('-started_at').first()

    if existing_attempt:
        active, remaining_seconds = is_session_active(existing_attempt.id)
        if active:
            return Response({
                'attempt_id': str(existing_attempt.id),
                'quiz_id': str(quiz.id),
                'quiz_title': quiz.title,
                'duration_minutes': quiz.time_limit_minutes,
                'remaining_seconds': remaining_seconds,
                'resumed': True,
                'message': 'Active quiz session resumed.'
            }, status=status.HTTP_200_OK)

    # Create new attempt record in PostgreSQL
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz
    )

    # Initialize Redis TTL key
    session_info = start_quiz_session(
        attempt_id=attempt.id,
        quiz_id=quiz.id,
        duration_minutes=quiz.time_limit_minutes,
        student_id=request.user.id
    )

    return Response({
        'attempt_id': str(attempt.id),
        'quiz_id': str(quiz.id),
        'quiz_title': quiz.title,
        'duration_minutes': quiz.time_limit_minutes,
        'started_at': session_info.get('started_at'),
        'expires_at': session_info.get('expires_at'),
        'remaining_seconds': quiz.time_limit_minutes * 60,
        'resumed': False,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_session(request, attempt_id):
    """
    Query remaining countdown time and session validity status in Redis [LMS-QZ-02].
    """
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id, student=request.user)
    except QuizAttempt.DoesNotExist:
        return Response({'error': 'Quiz attempt not found'}, status=status.HTTP_404_NOT_FOUND)

    if attempt.completed_at is not None:
        return Response({
            'attempt_id': str(attempt.id),
            'quiz_id': str(attempt.quiz_id),
            'is_active': False,
            'is_completed': True,
            'remaining_seconds': 0,
            'message': 'Quiz attempt has already been submitted.'
        }, status=status.HTTP_200_OK)

    active, remaining_seconds = is_session_active(attempt.id)
    return Response({
        'attempt_id': str(attempt.id),
        'quiz_id': str(attempt.quiz_id),
        'is_active': active,
        'is_completed': False,
        'remaining_seconds': remaining_seconds,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, attempt_id):
    """
    Submit quiz and calculate grade using ACID transactions [LMS-QZ-03].
    Submissions after Redis TTL expiry are automatically rejected [LMS-QZ-02].
    """
    try:
        attempt = QuizAttempt.objects.select_related('quiz').get(
            id=attempt_id, student=request.user
        )
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Quiz attempt not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if attempt.completed_at is not None:
        return Response(
            {'error': 'Quiz attempt already submitted'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify Redis TTL has not expired [LMS-QZ-02]
    active, remaining_seconds = is_session_active(attempt_id)
    if not active:
        return Response(
            {'error': 'Exam session has expired. Submission rejected.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    answers_data = request.data.get('answers', [])
    if not isinstance(answers_data, list):
        return Response(
            {'error': "Invalid payload format. 'answers' must be a list."},
            status=status.HTTP_400_BAD_REQUEST
        )

    quiz_questions = {str(q.id): q for q in attempt.quiz.questions.all()}
    total_questions = len(quiz_questions)
    total_points = sum(q.points for q in quiz_questions.values())

    try:
        with transaction.atomic():
            correct_count = 0
            earned_points = 0
            seen_questions = set()

            for ans in answers_data:
                question_id = str(ans.get('question_id', ''))
                option_id = str(ans.get('option_id', ''))

                if question_id not in quiz_questions:
                    raise ValidationError(
                        f"Question {question_id} does not belong to this quiz."
                    )

                if question_id in seen_questions:
                    raise ValidationError(
                        f"Duplicate answer submitted for question {question_id}."
                    )
                seen_questions.add(question_id)

                try:
                    selected_opt = Option.objects.get(
                        id=option_id,
                        question_id=question_id
                    )
                except Option.DoesNotExist:
                    raise ValidationError(
                        f"Option {option_id} does not belong to question {question_id}."
                    )

                StudentAnswer.objects.create(
                    attempt=attempt,
                    question_id=question_id,
                    selected_option=selected_opt
                )

                if selected_opt.is_correct:
                    correct_count += 1
                    earned_points += quiz_questions[question_id].points

            if total_points > 0:
                score_percent = int(round((earned_points / total_points) * 100))
            elif total_questions > 0:
                score_percent = int(round((correct_count / total_questions) * 100))
            else:
                score_percent = 0

            is_passed = score_percent >= attempt.quiz.passing_score

            attempt.total_score = score_percent
            attempt.is_passed = is_passed
            attempt.completed_at = timezone.now()
            attempt.save()

    except ValidationError as err:
        return Response(
            {'error': str(err.message if hasattr(err, 'message') else err)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as exc:
        return Response(
            {'error': f'Submission failed: {str(exc)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Clear active session key from Redis upon successful atomic commit
    clear_quiz_session(attempt_id)

    return Response({
        'attempt_id': str(attempt.id),
        'score': score_percent,
        'is_passed': is_passed,
        'correct_answers': correct_count,
        'total_questions': total_questions,
        'completed_at': attempt.completed_at.isoformat(),
    })
