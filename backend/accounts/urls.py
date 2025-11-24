from django.urls import path
from . import views

urlpatterns = [
    path('onboard/', views.onboard_user, name='onboard_user'),
    path('user-info/', views.user_info, name='user_info'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('payment/', views.create_stripe_session, name='create_stripe_session'),
]