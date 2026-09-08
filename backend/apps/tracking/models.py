import uuid
from django.db import models
from django.conf import settings
from apps.courses.models import Lesson


class LessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_progress')
    last_watched_second = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'lesson')
        indexes = [
            models.Index(fields=['student', 'lesson']),
        ]

    def __str__(self):
        status = "Completed" if self.is_completed else f"{self.last_watched_second}s"
        return f"{self.student.username} - {self.lesson.title}: {status}"
