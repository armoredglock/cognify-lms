from django.urls import path
from .views import start_quiz, submit_quiz

urlpatterns = [
    path('quizzes/<uuid:quiz_id>/start/', start_quiz, name='start_quiz'),
    path('attempts/<uuid:attempt_id>/submit/', submit_quiz, name='submit_quiz'),
]
