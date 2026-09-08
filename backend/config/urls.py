from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/tracking/', include('apps.tracking.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
    path('api/gamification/', include('apps.gamification.urls')),
    path('api/ai/', include('apps.ai_generator.urls')),
]
