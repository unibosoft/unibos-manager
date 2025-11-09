"""
Core app URLs
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/check/', views.check_auth, name='check_auth'),
    path('auth/user/', views.current_user, name='current_user'),
    path('auth/profile/', views.ProfileUpdateView.as_view(), name='profile'),
]