"""
Signal handlers for authentication app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

# Configure logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        try:
            UserProfile.objects.create(user=instance)
            logger.info(f"Created profile for user: {instance.username}")
        except Exception as e:
            logger.error(f"Failed to create profile for user {instance.username}: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when the User is saved.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    try:
        instance.profile.save()
        logger.debug(f"Saved profile for user: {instance.username}")
    except UserProfile.DoesNotExist:
        # Profile doesn't exist, create it
        try:
            UserProfile.objects.create(user=instance)
            logger.info(f"Created missing profile for user: {instance.username}")
        except Exception as e:
            logger.error(f"Failed to create missing profile for user {instance.username}: {e}")
    except Exception as e:
        logger.error(f"Failed to save profile for user {instance.username}: {e}") 