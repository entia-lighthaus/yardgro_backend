from django.contrib import admin
from .models import FarmerProfile, BuyerProfile, RecyclerProfile

admin.site.register(FarmerProfile)
admin.site.register(BuyerProfile)
admin.site.register(RecyclerProfile)

