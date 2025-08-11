from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    We no longer create role-specific profiles here.
    Profile creation is now handled directly in the RegistrationSerializer.
    """
    pass  # No action needed for now
