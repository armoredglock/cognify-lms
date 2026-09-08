import uuid
from django.db import models
from django.conf import settings
from apps.courses.models import Lesson


class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    time_limit_minutes = models.PositiveIntegerField(default=15, help_text="Duration in minutes managed via Redis TTL")
    passing_score = models.PositiveIntegerField(default=70, help_text="Minimum passing percentage")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    class Type(models.TextChoices):
        MCQ = 'MCQ', 'Multiple Choice'
        TRUE_FALSE = 'TRUE_FALSE', 'True / False'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=Type.choices, default=Type.MCQ)
    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"[{self.quiz.title}] {self.question_text[:50]}"


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_text} ({'Correct' if self.is_correct else 'Wrong'})"


class QuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    total_score = models.IntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}: {self.total_score}%"


class StudentAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('attempt', 'question')
