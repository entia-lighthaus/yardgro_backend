from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import FarmerProfile, BuyerProfile, RecyclerProfile

from profiles.serializers import (
    FarmerProfileUpdateSerializer,
    BuyerProfileUpdateSerializer,
    RecyclerProfileUpdateSerializer
)


User = get_user_model()

# Serializers for role-specific profiles

class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ['farm_name', 'location', 'products'] 



class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = ['buyer_type', 'company_name', 'address']



class RecyclerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecyclerProfile
        fields = ['user','company_name', 'materials_accepted']  



class UserDetailSerializer(serializers.ModelSerializer):
    farmer_profile = FarmerProfileSerializer(read_only=True)
    buyer_profile = BuyerProfileSerializer(read_only=True)
    recycler_profile = RecyclerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'date_joined',
            'farmer_profile',
            'buyer_profile',
            'recycler_profile',
        ]



# This serializer allows updating the user details and their associated profiles based on the role.
# It handles the nested updates for each profile type.
# It assumes that the user is authenticated and has permission to update their own details.
class UserUpdateSerializer(serializers.ModelSerializer):
    farmer_profile = FarmerProfileUpdateSerializer(required=False, allow_null=True)
    buyer_profile = BuyerProfileUpdateSerializer(required=False, allow_null=True)
    recycler_profile = RecyclerProfileUpdateSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'farmer_profile', 'buyer_profile', 'recycler_profile']

    def update(self, instance, validated_data):
        # Update base user fields only if provided
        if 'username' in validated_data:
            instance.username = validated_data['username']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        instance.save()

        # Role-specific updates
        if instance.role == 'farmer' and 'farmer_profile' in validated_data:
            farmer_data = validated_data.pop('farmer_profile', {})
            FarmerProfile.objects.update_or_create(user=instance, defaults=farmer_data)

        elif instance.role == 'buyer' and 'buyer_profile' in validated_data:
            buyer_data = validated_data.pop('buyer_profile', {})
            BuyerProfile.objects.update_or_create(user=instance, defaults=buyer_data)

        elif instance.role == 'recycler' and 'recycler_profile' in validated_data:
            recycler_data = validated_data.pop('recycler_profile', {})
            RecyclerProfile.objects.update_or_create(user=instance, defaults=recycler_data)

        return instance



#Registration serializer for creating users with role-specific profiles
# This serializer handles the creation of users and their associated profiles based on the role.
# It validates the role and ensures that the required fields for each profile type are provided.

class RegistrationSerializer(serializers.ModelSerializer):
    # Phone field - optional (stored in User model)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    # Buyer-specific fields
    buyer_type = serializers.ChoiceField(
        choices=[
            ('individual', 'Individual'),
            ('household', 'Household'),
            ('company', 'Company'),
        ],
        required=False
    )
    address = serializers.CharField(required=False)

    # Farmer-specific fields
    farm_name = serializers.CharField(required=False)
    location = serializers.CharField(required=False)  
    products = serializers.CharField(required=False)

    # Recycler-specific fields
    company_name = serializers.CharField(required=False)
    materials_accepted = serializers.CharField(required=False)
    
    password = serializers.CharField(write_only=True)
    


    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'role',
            # Profile fields (not stored in User model)
            'farm_name', 'location', 'products',

            'buyer_type', 'address',

            'company_name', 'materials_accepted',
        ]
    
    def validate_phone(self, value):
        """Validate phone number format (optional field)"""
        if not value:  # Skip validation if phone is empty/null
            return value
            
        # Basic format validation for non-empty values
        cleaned_phone = ''.join(filter(str.isdigit, value))
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10 and 15 digits."
            )
        return value
    
    def validate_role(self, value):
        """Ensure role is valid"""
        valid_roles = ['farmer', 'buyer', 'recycler']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {valid_roles}")
        return value
    
    def validate(self, attrs):
        """Cross-field validation based on role"""
        role = attrs.get('role')
        buyer_type = attrs.get('buyer_type')
        
        # Clean up empty strings - convert to None for optional fields
        optional_fields = ['company_name', 'farm_name', 'location', 'products', 'materials_accepted', 'address']
        for field in optional_fields:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        # Role-specific validations
        if role == 'buyer':
            if not buyer_type:
                raise serializers.ValidationError({
                    'buyer_type': 'Buyer type is required for buyers.'
                })
                
            if buyer_type == 'company' and not attrs.get('company_name'):
                raise serializers.ValidationError({
                    'company_name': 'Company name is required for company buyers.'
                })
                    
        return attrs
    
    def create(self, validated_data):
        # Extract role and password
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        
        # Extract profile-specific fields (not stored in User model)
        profile_data = {}
        profile_fields = ['farm_name', 'location', 'products', 'buyer_type', 'address', 'company_name', 'materials_accepted']
        
        for field in profile_fields:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)
        
        # Create user (phone is optional and can be None/empty)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone'),  # Phone is optional
            password=password,
            role=role
        )
        
        # Create role-specific profile
        try:
            if role == 'buyer':
                buyer_profile_data = {'user': user}
                for field in ['buyer_type', 'company_name', 'address']:
                    if field in profile_data and profile_data[field] is not None:
                        buyer_profile_data[field] = profile_data[field]
                BuyerProfile.objects.create(**buyer_profile_data)
                
            elif role == 'farmer':
                farmer_profile_data = {'user': user}
                for field in ['farm_name', 'location', 'products']:
                    if field in profile_data and profile_data[field] is not None:
                        farmer_profile_data[field] = profile_data[field]
                FarmerProfile.objects.create(**farmer_profile_data)
                
            elif role == 'recycler':
                recycler_profile_data = {'user': user}
                for field in ['company_name', 'materials_accepted']:
                    if field in profile_data and profile_data[field] is not None:
                        recycler_profile_data[field] = profile_data[field]
                RecyclerProfile.objects.create(**recycler_profile_data)
                
        except Exception as profile_error:
            user.delete()  # Clean up if profile creation fails
            raise serializers.ValidationError(f"Profile creation failed: {str(profile_error)}")
        
        return user