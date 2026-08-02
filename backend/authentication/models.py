"""
Authentication models for Kwantum Institute.
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from django.utils import timezone
from typing import Optional


class UserProfile(models.Model):
    """
    Extended user profile model for additional user information.
    
    This model extends the default Django User model with additional
    fields specific to the Kwantum Institute platform.
    """
    
    user: User = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    bio: str = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="User's biography or description"
    )
    
    avatar: Optional[str] = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        help_text="User's profile picture"
    )
    
    date_of_birth: Optional[models.DateField] = models.DateField(
        blank=True, 
        null=True,
        help_text="User's date of birth"
    )
    
    phone_number: str = models.CharField(
        max_length=20, 
        blank=True,
        help_text="User's phone number"
    )
    
    is_verified: bool = models.BooleanField(
        default=False,
        help_text="Whether the user's email has been verified"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="When the profile was created"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="When the profile was last updated"
    )
    
    class Meta:
        """Meta options for UserProfile model."""
        verbose_name: str = "User Profile"
        verbose_name_plural: str = "User Profiles"
        ordering: list[str] = ['-created_at']
    
    def __str__(self) -> str:
        """String representation of the user profile."""
        return f"Profile for {self.user.username}"
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class LoginAttempt(models.Model):
    """
    Model to track login attempts for security monitoring.
    
    This model helps track failed login attempts and can be used
    for implementing rate limiting and security measures.
    """
    
    username: str = models.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        help_text="Username used in the login attempt"
    )
    
    ip_address: str = models.GenericIPAddressField(
        help_text="IP address of the login attempt"
    )
    
    user_agent: str = models.TextField(
        blank=True,
        help_text="User agent string from the request"
    )
    
    success: bool = models.BooleanField(
        default=False,
        help_text="Whether the login attempt was successful"
    )
    
    timestamp: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="When the login attempt occurred"
    )
    
    class Meta:
        """Meta options for LoginAttempt model."""
        verbose_name: str = "Login Attempt"
        verbose_name_plural: str = "Login Attempts"
        ordering: list[str] = ['-timestamp']
        indexes: list[models.Index] = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self) -> str:
        """String representation of the login attempt."""
        status = "Success" if self.success else "Failed"
        return f"{status} login attempt for {self.username} at {self.timestamp}"


class PasswordResetToken(models.Model):
    """
    Model for managing password reset tokens.
    
    This model stores temporary tokens used for password reset
    functionality with automatic expiration.
    """
    
    user: User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text="User requesting password reset"
    )
    
    token: str = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique token for password reset"
    )
    
    is_used: bool = models.BooleanField(
        default=False,
        help_text="Whether the token has been used"
    )
    
    expires_at: models.DateTimeField = models.DateTimeField(
        help_text="When the token expires"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="When the token was created"
    )
    
    class Meta:
        """Meta options for PasswordResetToken model."""
        verbose_name: str = "Password Reset Token"
        verbose_name_plural: str = "Password Reset Tokens"
        ordering: list[str] = ['-created_at']
        indexes: list[models.Index] = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self) -> str:
        """String representation of the password reset token."""
        return f"Password reset token for {self.user.username}"
    
    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if the token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired 