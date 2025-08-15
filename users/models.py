from django.db import models
from django.contrib.auth.models import AbstractUser


# This Holds the custom user model (login, authentication, role field).
# Custom User Model

class User(AbstractUser):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('recycler', 'Recycler'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    #phone = models.CharField(max_length=20, unique=True) 
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    

