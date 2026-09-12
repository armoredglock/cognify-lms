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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def review_quiz_attempt(request, attempt_id):
    """
    Retrieve question-by-question review for a submitted quiz attempt [LMS-QZ-04].
    Prevents leakage before submission and enforces student ownership.
    """
    try:
        attempt = QuizAttempt.objects.select_related(
            'quiz', 'student'
        ).prefetch_related(
            'student_answers__selected_option',
            'student_answers__question',
            'quiz__questions__options'
        ).get(id=attempt_id)
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Quiz attempt not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Permission check: student can only review their own attempt (or staff)
    if attempt.student != request.user and not request.user.is_staff:
        return Response(
            {'error': 'Quiz attempt not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Prevent answer leakage before submission
    if attempt.completed_at is None:
        return Response(
            {
                'error': (
                    'Quiz attempt is still in progress. '
                    'Review is only available after submission.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    answers_map = {
        sa.question_id: sa
        for sa in attempt.student_answers.all()
    }

    questions_review = []
    for question in attempt.quiz.questions.all():
        student_ans = answers_map.get(question.id)
        correct_opt = question.correct_option
        is_correct = bool(
            student_ans and student_ans.selected_option.is_correct
        )
        earned_points = question.points if is_correct else 0

        questions_review.append({
            'question_id': str(question.id),
            'question_text': question.question_text,
            'question_type': question.question_type,
            'points_possible': question.points,
            'points_earned': earned_points,
            'is_correct': is_correct,
            'selected_option': {
                'id': str(student_ans.selected_option.id),
                'option_text': student_ans.selected_option.option_text,
            } if student_ans else None,
            'correct_option': {
                'id': str(correct_opt.id),
                'option_text': correct_opt.option_text,
            } if correct_opt else None,
            'options': [
                {
                    'id': str(opt.id),
                    'option_text': opt.option_text,
                    'is_correct': opt.is_correct,
                }
                for opt in question.options.all()
            ],
        })

    return Response({
        'attempt_id': str(attempt.id),
        'quiz_id': str(attempt.quiz.id),
        'quiz_title': attempt.quiz.title,
        'student_username': attempt.student.username,
        'score': attempt.total_score,
        'passing_score': attempt.quiz.passing_score,
        'is_passed': attempt.is_passed,
        'started_at': attempt.started_at.isoformat(),
        'completed_at': attempt.completed_at.isoformat(),
        'questions': questions_review,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_history(request, quiz_id):
    """
    Retrieve historical completed attempts for the authenticated student [LMS-QZ-04].
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        completed_at__isnull=False
    ).order_by('-completed_at')

    history_records = [
        {
            'attempt_id': str(att.id),
            'score': att.total_score,
            'passing_score': quiz.passing_score,
            'is_passed': att.is_passed,
            'started_at': att.started_at.isoformat(),
            'completed_at': att.completed_at.isoformat(),
        }
        for att in attempts
    ]

    return Response({
        'quiz_id': str(quiz.id),
        'quiz_title': quiz.title,
        'passing_score': quiz.passing_score,
        'total_attempts': len(history_records),
        'attempts': history_records,
    })
