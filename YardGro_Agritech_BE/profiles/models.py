from django.db import models
from django.conf import settings


# Role-Specific Profiles
# One-to-One relationships so each user can have exactly one profile for their role.

#FARMER PROFILE
class FarmerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    farm_name = models.CharField(max_length=255)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in acres or hectares")
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.farm_name



# BUYER PROFILE
# This profile can be for individuals or companies
class BuyerProfile(models.Model):
    BUYER_TYPE_CHOICES = [
        ('individual', 'Individual/Household'),
        ('company', 'Company'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.company_name or self.user.username



# RECYCLER PROFILE
# This profile can be for individuals or recycling companies
# It can include details about the types of materials they recycle
class RecyclerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recycling_focus = models.TextField(help_text="Describe the type of materials recycled")

    def __str__(self):
        return f"Recycler: {self.user.username}"

