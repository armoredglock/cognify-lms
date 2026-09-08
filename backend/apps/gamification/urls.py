from django.urls import path
from .views import course_leaderboard, issue_certificate

urlpatterns = [
    path('leaderboard/<uuid:course_id>/', course_leaderboard, name='course_leaderboard'),
    path('certificates/<uuid:course_id>/issue/', issue_certificate, name='issue_certificate'),
]
