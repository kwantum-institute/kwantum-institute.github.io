"""
API URL configuration for authentication app.
"""
from django.urls import path
from . import views

app_name: str = 'auth_api'

urlpatterns: list = [
    # Authentication endpoints
    path('auth/login/', views.LoginView.as_view(), name='api_login'),
    path('auth/logout/', views.LogoutView.as_view(), name='api_logout'),
    path('auth/register/', views.RegisterView.as_view(), name='api_register'),
    
    # User profile management
    path('auth/profile/', views.UserProfileView.as_view(), name='api_profile'),
    path('auth/user-info/', views.user_info, name='api_user_info'),
    
    # Password management
    path('auth/password/change/', views.PasswordChangeView.as_view(), name='api_password_change'),
    path('auth/password/reset/', views.PasswordResetRequestView.as_view(), name='api_password_reset_request'),
    path('auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='api_password_reset_confirm'),
    
    # Authentication status
    path('auth/check-auth/', views.check_auth, name='api_check_auth'),
] 