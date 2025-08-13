from rest_framework import serializers
from .models import FarmerProfile, BuyerProfile, RecyclerProfile

class FarmerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = '__all__'  # Or list specific fields required for update

class BuyerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = '__all__'

class RecyclerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecyclerProfile
        fields = '__all__'
