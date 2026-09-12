from rest_framework import serializers
from .models import Quiz, Question, Option, QuizAttempt, StudentAnswer


class OptionSerializer(serializers.ModelSerializer):
    """Option serializer for student test taking (hides correctness)."""
    class Meta:
        model = Option
        fields = ['id', 'option_text']


class OptionReviewSerializer(serializers.ModelSerializer):
    """Option serializer for post-submission review (includes is_correct)."""
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    """Question serializer with option choices."""
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'points', 'options']


class QuizSerializer(serializers.ModelSerializer):
    """Quiz serializer with metadata and question list."""
    questions = QuestionSerializer(many=True, read_only=True)
    total_points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'lesson',
            'title',
            'time_limit_minutes',
            'passing_score',
            'total_points',
            'questions',
            'created_at',
        ]


class StudentAnswerSerializer(serializers.ModelSerializer):
    """Student answer record."""
    class Meta:
        model = StudentAnswer
        fields = ['id', 'attempt', 'question', 'selected_option', 'answered_at']
        read_only_fields = ['id', 'answered_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Quiz attempt summary serializer."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id',
            'student',
            'student_username',
            'quiz',
            'quiz_title',
            'total_score',
            'is_passed',
            'started_at',
            'completed_at',
        ]
        read_only_fields = ['id', 'total_score', 'is_passed', 'started_at', 'completed_at']
