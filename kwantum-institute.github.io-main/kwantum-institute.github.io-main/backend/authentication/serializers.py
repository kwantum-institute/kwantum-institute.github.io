"""
Serializers for authentication API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from typing import Dict, Any, Optional
from .models import UserProfile, LoginAttempt, PasswordResetToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Provides safe serialization of user data for API responses.
    """
    
    class Meta:
        """Meta configuration for UserSerializer."""
        model: type[User] = User
        fields: list[str] = [
            'id', 'username', 'email', 'first_name', 
            'last_name', 'date_joined', 'is_active'
        ]
        read_only_fields: list[str] = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    
    Includes nested user data and handles profile-specific fields.
    """
    
    user: UserSerializer = UserSerializer(read_only=True)
    full_name: str = serializers.CharField(read_only=True)
    
    class Meta:
        """Meta configuration for UserProfileSerializer."""
        model: type[UserProfile] = UserProfile
        fields: list[str] = [
            'id', 'user', 'bio', 'avatar', 'date_of_birth',
            'phone_number', 'is_verified', 'created_at', 
            'updated_at', 'full_name'
        ]
        read_only_fields: list[str] = ['id', 'created_at', 'updated_at', 'full_name']


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Handles username/password authentication and returns user data.
    """
    
    username: str = serializers.CharField(
        max_length=150,
        help_text="Username for authentication"
    )
    password: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="Password for authentication"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate login credentials.
        
        Args:
            attrs: Dictionary containing username and password
            
        Returns:
            Dictionary with validated data
            
        Raises:
            ValidationError: If credentials are invalid
        """
        username: str = attrs.get('username')
        password: str = attrs.get('password')
        
        if username and password:
            user: Optional[User] = authenticate(
                username=username, 
                password=password
            )
            
            if not user:
                raise ValidationError(
                    "Invalid username or password."
                )
            
            if not user.is_active:
                raise ValidationError(
                    "User account is disabled."
                )
            
            attrs['user'] = user
        else:
            raise ValidationError(
                "Must include 'username' and 'password'."
            )
        
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles new user creation with validation and profile creation.
    """
    
    password: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="Password for the new account"
    )
    password_confirm: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="Password confirmation"
    )
    
    class Meta:
        """Meta configuration for RegisterSerializer."""
        model: type[User] = User
        fields: list[str] = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        ]
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate registration data.
        
        Args:
            attrs: Dictionary containing registration data
            
        Returns:
            Dictionary with validated data
            
        Raises:
            ValidationError: If validation fails
        """
        password: str = attrs.get('password')
        password_confirm: str = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise ValidationError(
                "Passwords do not match."
            )
        
        # Check if username already exists
        username: str = attrs.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                "Username already exists."
            )
        
        # Check if email already exists
        email: str = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Email already exists."
            )
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new user and profile.
        
        Args:
            validated_data: Validated registration data
            
        Returns:
            Newly created User instance
        """
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
        # Create user (UserProfile will be created automatically by signal)
        user: User = User.objects.create_user(**validated_data)
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    
    Handles password change with old password verification.
    """
    
    old_password: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="Current password"
    )
    new_password: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="New password"
    )
    new_password_confirm: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="New password confirmation"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate password change data.
        
        Args:
            attrs: Dictionary containing password change data
            
        Returns:
            Dictionary with validated data
            
        Raises:
            ValidationError: If validation fails
        """
        new_password: str = attrs.get('new_password')
        new_password_confirm: str = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise ValidationError(
                "New passwords do not match."
            )
        
        return attrs
    
    def validate_old_password(self, value: str) -> str:
        """
        Validate that the old password is correct.
        
        Args:
            value: Old password value
            
        Returns:
            Validated old password
            
        Raises:
            ValidationError: If old password is incorrect
        """
        user: User = self.context['request'].user
        
        if not user.check_password(value):
            raise ValidationError(
                "Current password is incorrect."
            )
        
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    
    Handles email-based password reset requests.
    """
    
    email: str = serializers.EmailField(
        help_text="Email address for password reset"
    )
    
    def validate_email(self, value: str) -> str:
        """
        Validate that the email exists in the system.
        
        Args:
            value: Email address
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If email doesn't exist
        """
        if not User.objects.filter(email=value, is_active=True).exists():
            raise ValidationError(
                "No active user found with this email address."
            )
        
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    
    Handles password reset with token verification.
    """
    
    token: str = serializers.CharField(
        max_length=100,
        help_text="Password reset token"
    )
    new_password: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="New password"
    )
    new_password_confirm: str = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="New password confirmation"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate password reset confirmation data.
        
        Args:
            attrs: Dictionary containing password reset data
            
        Returns:
            Dictionary with validated data
            
        Raises:
            ValidationError: If validation fails
        """
        new_password: str = attrs.get('new_password')
        new_password_confirm: str = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise ValidationError(
                "Passwords do not match."
            )
        
        return attrs
    
    def validate_token(self, value: str) -> str:
        """
        Validate that the token is valid and not expired.
        
        Args:
            value: Token value
            
        Returns:
            Validated token
            
        Raises:
            ValidationError: If token is invalid or expired
        """
        try:
            token_obj: PasswordResetToken = PasswordResetToken.objects.get(
                token=value
            )
            
            if not token_obj.is_valid:
                raise ValidationError(
                    "Token is invalid or has expired."
                )
            
        except PasswordResetToken.DoesNotExist:
            raise ValidationError(
                "Invalid token."
            )
        
        return value 