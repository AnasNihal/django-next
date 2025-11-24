from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from automations.views import AutomationViewSet, KeywordViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'automations', AutomationViewSet, basename='automation')
router.register(r'keywords', KeywordViewSet, basename='keyword')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/', include(router.urls)),
    path('api/accounts/', include('accounts.urls')),
    path('api/integrations/', include('integrations.urls')),
    path('api/webhooks/', include('webhooks.urls')),
]