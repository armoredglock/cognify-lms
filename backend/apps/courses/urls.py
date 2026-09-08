from django.urls import path
from .views import list_courses, enroll_course

urlpatterns = [
    path('', list_courses, name='course_list'),
    path('<uuid:course_id>/enroll/', enroll_course, name='course_enroll'),
]
