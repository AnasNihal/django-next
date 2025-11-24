from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_integrations, name='get_integrations'),
    path('integrate/', views.integrate_instagram, name='integrate_instagram'),
    path('posts/', views.get_profile_posts, name='get_profile_posts'),
]