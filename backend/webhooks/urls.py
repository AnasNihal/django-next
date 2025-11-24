from django.urls import path
from . import views

urlpatterns = [
    path('instagram/', views.instagram_webhook, name='instagram_webhook'),
]