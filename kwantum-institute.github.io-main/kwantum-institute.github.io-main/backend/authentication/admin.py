"""
Admin configuration for authentication app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, LoginAttempt, PasswordResetToken


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile model.
    
    Displays user profile information inline with user admin.
    """
    
    model: type = UserProfile
    can_delete: bool = False
    verbose_name_plural: str = 'Profile'
    fk_name: str = 'user'


class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with inline profile.
    
    Extends the default User admin to include profile information.
    """
    
    inlines: list = [UserProfileInline]
    
    def get_inline_instances(self, request, obj=None):
        """
        Get inline instances for the admin form.
        
        Args:
            request: HTTP request object
            obj: User object being edited
            
        Returns:
            List of inline instances
        """
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    
    Provides admin interface for managing user profiles.
    """
    
    list_display: list[str] = [
        'user', 'full_name', 'is_verified', 'created_at', 'updated_at'
    ]
    list_filter: list[str] = ['is_verified', 'created_at', 'updated_at']
    search_fields: list[str] = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields: list[str] = ['created_at', 'updated_at', 'full_name']
    
    fieldsets: tuple = (
        ('User Information', {
            'fields': ('user', 'full_name')
        }),
        ('Profile Details', {
            'fields': ('bio', 'avatar', 'date_of_birth', 'phone_number')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj: UserProfile) -> str:
        """
        Get the full name of the user.
        
        Args:
            obj: UserProfile instance
            
        Returns:
            User's full name
        """
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Admin configuration for LoginAttempt model.
    
    Provides admin interface for monitoring login attempts.
    """
    
    list_display: list[str] = [
        'username', 'ip_address', 'success', 'timestamp'
    ]
    list_filter: list[str] = ['success', 'timestamp']
    search_fields: list[str] = ['username', 'ip_address']
    readonly_fields: list[str] = ['timestamp']
    
    fieldsets: tuple = (
        ('Login Information', {
            'fields': ('username', 'ip_address', 'success')
        }),
        ('Request Details', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request) -> bool:
        """
        Disable manual creation of login attempts.
        
        Args:
            request: HTTP request object
            
        Returns:
            False to disable manual creation
        """
        return False
    
    def has_change_permission(self, request, obj=None) -> bool:
        """
        Disable editing of login attempts.
        
        Args:
            request: HTTP request object
            obj: LoginAttempt instance
            
        Returns:
            False to disable editing
        """
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetToken model.
    
    Provides admin interface for managing password reset tokens.
    """
    
    list_display: list[str] = [
        'user', 'token', 'is_used', 'is_expired', 'created_at', 'expires_at'
    ]
    list_filter: list[str] = ['is_used', 'created_at', 'expires_at']
    search_fields: list[str] = ['user__username', 'user__email', 'token']
    readonly_fields: list[str] = ['created_at', 'is_expired', 'is_valid']
    
    fieldsets: tuple = (
        ('Token Information', {
            'fields': ('user', 'token', 'is_used')
        }),
        ('Expiration', {
            'fields': ('expires_at', 'is_expired', 'is_valid')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj: PasswordResetToken) -> bool:
        """
        Check if token is expired.
        
        Args:
            obj: PasswordResetToken instance
            
        Returns:
            True if token is expired
        """
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def is_valid(self, obj: PasswordResetToken) -> bool:
        """
        Check if token is valid.
        
        Args:
            obj: PasswordResetToken instance
            
        Returns:
            True if token is valid
        """
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin) 