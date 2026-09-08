import uuid
from django.db import models
from django.conf import settings
from apps.courses.models import Course


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='issued_certificates')
    verification_hash = models.CharField(max_length=64, unique=True, db_index=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.course.title} ({self.verification_hash[:8]})"
