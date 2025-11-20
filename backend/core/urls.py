"""
Core URLs for health checks and system monitoring.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health-check'),
    path('db/', views.database_check, name='database-check'),
    path('cache/', views.cache_check, name='cache-check'),
]
