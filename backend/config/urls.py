"""
URL configuration for FlowPilot AI project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_v1_patterns = [
    path('auth/', include('apps.users.urls')),
    path('users/', include('apps.users.urls_users')),
    path('organizations/', include('apps.organizations.urls')),
    path('workflows/', include('apps.workflows.urls')),
    path('executions/', include('apps.executions.urls')),
    path('ai/', include('apps.ai_engine.urls')),
    path('connectors/', include('apps.connectors.urls')),
    path('documents/', include('apps.documents.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('billing/', include('apps.billing.urls')),
    path('sso/', include('apps.sso.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include(api_v1_patterns)),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Health check
    path('health/', include('core.urls')),
]

# Debug toolbar in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'FlowPilot AI Administration'
admin.site.site_title = 'FlowPilot AI Admin'
admin.site.index_title = 'Welcome to FlowPilot AI Administration'
