"""
API views for authentication functionality.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from typing import Dict, Any
import logging

from .serializers import (
    UserSerializer, UserProfileSerializer, LoginSerializer,
    RegisterSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .models import UserProfile, LoginAttempt, PasswordResetToken

# Configure logging
logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    API view for user login.
    
    Handles user authentication and returns user data with session.
    """
    
    permission_classes: list = [permissions.AllowAny]
    
    def post(self, request) -> Response:
        """
        Handle user login.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with user data and authentication status
        """
        serializer: LoginSerializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user: User = serializer.validated_data['user']
            
            # Log the user in
            login(request, user)
            
            # Create or get token for API access
            token, created = Token.objects.get_or_create(user=user)
            
            # Log login attempt
            self._log_login_attempt(request, user.username, True)
            
            # Get user profile
            try:
                profile: UserProfile = user.profile
                profile_serializer: UserProfileSerializer = UserProfileSerializer(profile)
                profile_data: Dict[str, Any] = profile_serializer.data
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile: UserProfile = UserProfile.objects.create(user=user)
                profile_serializer: UserProfileSerializer = UserProfileSerializer(profile)
                profile_data: Dict[str, Any] = profile_serializer.data
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'profile': profile_data,
                'token': token.key,
            }, status=status.HTTP_200_OK)
        else:
            # Log failed login attempt
            username: str = request.data.get('username', 'unknown')
            self._log_login_attempt(request, username, False)
            
            return Response({
                'success': False,
                'message': 'Login failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _log_login_attempt(self, request, username: str, success: bool) -> None:
        """
        Log login attempt for security monitoring.
        
        Args:
            request: HTTP request object
            username: Username used in login attempt
            success: Whether login was successful
        """
        try:
            LoginAttempt.objects.create(
                username=username,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=success
            )
        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")


class LogoutView(APIView):
    """
    API view for user logout.
    
    Handles user logout and token deletion.
    """
    
    permission_classes: list = [permissions.IsAuthenticated]
    
    def post(self, request) -> Response:
        """
        Handle user logout.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with logout confirmation
        """
        try:
            # Delete the user's token
            request.user.auth_token.delete()
        except Exception:
            pass  # Token might not exist
        
        # Log the user out
        logout(request)
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    API view for user registration.
    
    Handles new user creation with profile setup.
    """
    
    permission_classes: list = [permissions.AllowAny]
    
    def post(self, request) -> Response:
        """
        Handle user registration.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with registration status
        """
        serializer: RegisterSerializer = RegisterSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user: User = serializer.save()
            
            # Log the user in after registration
            login(request, user)
            
            # Create token for API access
            token, created = Token.objects.get_or_create(user=user)
            
            # Get user profile
            profile: UserProfile = user.profile
            profile_serializer: UserProfileSerializer = UserProfileSerializer(profile)
            
            return Response({
                'success': True,
                'message': 'Registration successful',
                'user': UserSerializer(user).data,
                'profile': profile_serializer.data,
                'token': token.key,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Registration failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile management.
    
    Allows users to view and update their profile information.
    """
    
    serializer_class: type = UserProfileSerializer
    permission_classes: list = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Get the user's profile object.
        
        Returns:
            UserProfile instance for the current user
        """
        return self.request.user.profile


class PasswordChangeView(APIView):
    """
    API view for password change.
    
    Handles password change with old password verification.
    """
    
    permission_classes: list = [permissions.IsAuthenticated]
    
    def post(self, request) -> Response:
        """
        Handle password change.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with password change status
        """
        serializer: PasswordChangeSerializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user: User = request.user
            new_password: str = serializer.validated_data['new_password']
            
            # Change the password
            user.set_password(new_password)
            user.save()
            
            # Update or create new token
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'message': 'Password changed successfully',
                'token': token.key,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Password change failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API view for password reset request.
    
    Handles email-based password reset requests.
    """
    
    permission_classes: list = [permissions.AllowAny]
    
    def post(self, request) -> Response:
        """
        Handle password reset request.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with password reset request status
        """
        serializer: PasswordResetRequestSerializer = PasswordResetRequestSerializer(
            data=request.data
        )
        
        if serializer.is_valid():
            email: str = serializer.validated_data['email']
            user: User = User.objects.get(email=email)
            
            # Generate reset token
            token: str = get_random_string(64)
            expires_at: timezone.datetime = timezone.now() + timezone.timedelta(hours=24)
            
            # Create or update reset token
            PasswordResetToken.objects.filter(user=user).delete()
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # Send reset email (in production, implement proper email sending)
            reset_url: str = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            
            try:
                send_mail(
                    subject='Password Reset Request - Kwantum Institute',
                    message=f'''
                    Hello {user.username},
                    
                    You have requested a password reset for your Kwantum Institute account.
                    
                    Click the following link to reset your password:
                    {reset_url}
                    
                    This link will expire in 24 hours.
                    
                    If you did not request this reset, please ignore this email.
                    
                    Best regards,
                    Kwantum Institute Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send password reset email: {e}")
            
            return Response({
                'success': True,
                'message': 'Password reset email sent successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Password reset request failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API view for password reset confirmation.
    
    Handles password reset with token verification.
    """
    
    permission_classes: list = [permissions.AllowAny]
    
    def post(self, request) -> Response:
        """
        Handle password reset confirmation.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response with password reset confirmation status
        """
        serializer: PasswordResetConfirmSerializer = PasswordResetConfirmSerializer(
            data=request.data
        )
        
        if serializer.is_valid():
            token: str = serializer.validated_data['token']
            new_password: str = serializer.validated_data['new_password']
            
            # Get the token object
            token_obj: PasswordResetToken = PasswordResetToken.objects.get(token=token)
            user: User = token_obj.user
            
            # Change the password
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            token_obj.is_used = True
            token_obj.save()
            
            return Response({
                'success': True,
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Password reset failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request) -> Response:
    """
    Get current user information.
    
    Args:
        request: HTTP request object
        
    Returns:
        Response with current user data
    """
    user: User = request.user
    
    try:
        profile: UserProfile = user.profile
        profile_serializer: UserProfileSerializer = UserProfileSerializer(profile)
        profile_data: Dict[str, Any] = profile_serializer.data
    except UserProfile.DoesNotExist:
        profile: UserProfile = UserProfile.objects.create(user=user)
        profile_serializer: UserProfileSerializer = UserProfileSerializer(profile)
        profile_data: Dict[str, Any] = profile_serializer.data
    
    return Response({
        'success': True,
        'user': UserSerializer(user).data,
        'profile': profile_data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_auth(request) -> Response:
    """
    Check if user is authenticated.
    
    Args:
        request: HTTP request object
        
    Returns:
        Response with authentication status
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'authenticated': False
        }, status=status.HTTP_401_UNAUTHORIZED)


def _get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: HTTP request object
        
    Returns:
        Client's IP address as string
    """
    x_forwarded_for: str = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip: str = x_forwarded_for.split(',')[0]
    else:
        ip: str = request.META.get('REMOTE_ADDR')
    return ip 