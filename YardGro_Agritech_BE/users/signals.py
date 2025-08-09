from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from profiles.models import FarmerProfile, BuyerProfile, RecyclerProfile



# When a new user registers, we first create a User with their role.
# Then, based on the role, we automatically create the correct profile.
# This is done with Django signals in signals.py.

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'farmer':
            FarmerProfile.objects.create(user=instance)
        elif instance.role == 'buyer':
            BuyerProfile.objects.create(user=instance)
        elif instance.role == 'recycler':
            RecyclerProfile.objects.create(user=instance)
