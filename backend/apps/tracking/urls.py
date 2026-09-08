from django.urls import path
from .views import playback_heartbeat, sync_lesson_progress

urlpatterns = [
    path('heartbeat/', playback_heartbeat, name='playback_heartbeat'),
    path('lessons/<uuid:lesson_id>/sync/', sync_lesson_progress, name='sync_lesson_progress'),
]
