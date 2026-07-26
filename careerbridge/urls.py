"""
URL configuration for the careerbridge project.
Each app owns its own urls.py; this file just wires them together
under a namespace prefix, and serves media files in development.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('opportunities/', include('opportunities.urls')),
    path('applications/', include('applications.urls')),
    path('matching/', include('matching.urls')),
    path('notifications/', include('notifications.urls')),
    path('messages/', include('messaging.urls')),
    path('dashboard/', include('dashboard.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
