from django.contrib import admin
from .models import AIAssessmentArtifact

@admin.register(AIAssessmentArtifact)
class AIAssessmentArtifactAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'artifact_type', 'created_at')
    list_filter = ('artifact_type', 'created_at')
    search_fields = ('lesson__title',)
    readonly_fields = ('id', 'created_at')
