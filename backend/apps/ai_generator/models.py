import uuid
from django.db import models
from apps.courses.models import Lesson


class AIAssessmentArtifact(models.Model):
    class ArtifactType(models.TextChoices):
        QUIZ = 'QUIZ', 'Generated Quiz'
        FLASHCARD = 'FLASHCARD', 'Flashcards'
        SUMMARY = 'SUMMARY', 'Study Summary'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ai_artifacts')
    artifact_type = models.CharField(max_length=20, choices=ArtifactType.choices, default=ArtifactType.QUIZ)
    content = models.JSONField(help_text="Structured JSON containing generated questions or flashcard pairs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Artifact [{self.artifact_type}] - {self.lesson.title}"
