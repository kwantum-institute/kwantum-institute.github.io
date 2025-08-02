"""
URL configuration for authentication app.
"""
from django.urls import path
from . import views

app_name: str = 'authentication'

urlpatterns: list = [
    # Authentication endpoints
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('user-info/', views.user_info, name='user_info'),
    
    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Authentication status
    path('check-auth/', views.check_auth, name='check_auth'),
] 