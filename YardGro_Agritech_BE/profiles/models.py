from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL  # Custom user model


# Role-Specific Profiles
# One-to-One relationships so each user can have exactly one profile for their role.

# BUYER PROFILE
# This profile can be for individuals or companies
class BuyerProfile(models.Model):
    BUYER_TYPE_CHOICES = [
    ('individual', 'Individual'),
    ('household', 'Household'),
    ('vendor', 'Vendor'),
]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES, default='individual')
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        name_display = self.company_name if self.company_name else self.user.username
        return f"{name_display} ({self.buyer_type})"



#FARMER PROFILE
class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    products = models.TextField(blank=True, null=True)  # Could be JSON in future

    def __str__(self):
        name_display = self.farm_name if self.farm_name else self.user.username
        return f"{name_display} (Farmer)"
    



# RECYCLER PROFILE
# This profile can be for individuals or recycling companies
# It can include details about the types of materials they recycle
class RecyclerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recycler_profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    materials_accepted = models.TextField(blank=True, null=True)  # Could be JSON later

    def __str__(self):
        name_display = self.company_name if self.company_name else self.user.username
        return f"{name_display} (Recycler)"