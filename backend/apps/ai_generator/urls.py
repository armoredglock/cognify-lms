from django.urls import path
from .views import generate_lesson_ai_materials

urlpatterns = [
    path('lessons/<uuid:lesson_id>/generate/', generate_lesson_ai_materials, name='generate_lesson_ai_materials'),
]
