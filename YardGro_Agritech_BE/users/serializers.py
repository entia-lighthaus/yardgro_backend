from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import FarmerProfile, BuyerProfile, RecyclerProfile

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



#Registration serializer for creating users with role-specific profiles
# This serializer handles the creation of users and their associated profiles based on the role.
# It validates the role and ensures that the required fields for each profile type are provided.

class RegistrationSerializer(serializers.ModelSerializer):
    # Buyer-specific
    buyer_type = serializers.ChoiceField(
        choices=[
            ('individual', 'Individual'),
            ('household', 'Household'),
            ('vendor', 'Vendor'),
        ],
        required=False
    )
    contact_person = serializers.CharField(required=False)
    
    # Farmer-specific
    farm_name = serializers.CharField(required=False)
    location = serializers.CharField(required=False)  # Changed from farm_location
    crops_grown = serializers.CharField(required=False)
    
    # Recycler-specific
    company_name = serializers.CharField(required=False)
    materials_accepted = serializers.CharField(required=False)  # Changed from recycling_capacity
    
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'role',
            # Farmer
            'farm_name', 'location', 'crops_grown',
            # Buyer
            'buyer_type', 'contact_person',
            # Recycler  
            'company_name', 'materials_accepted',
        ]
    
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
        optional_fields = ['company_name', 'contact_person', 'farm_name', 'location', 'crops_grown', 'materials_accepted']
        for field in optional_fields:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        if role == 'buyer':
            # Only vendors require company_name
            if buyer_type == 'vendor':
                if not attrs.get('company_name'):
                    raise serializers.ValidationError({
                        'company_name': 'Company name is required for vendors.'
                    })
            # For individuals and households, company_name is optional
            elif buyer_type in ['individual', 'household']:
                # Company name is optional - can be provided or not
                pass
                
        elif role == 'farmer':
            # Farmer validation - all fields optional for now
            pass
        elif role == 'recycler':
            # Recycler validation - all fields optional for now
            pass
            
        return attrs
    
    def create(self, validated_data):
        # Extract role and profile-specific data
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        
        # Extract profile-specific fields (these aren't User model fields)
        profile_data = {}
        profile_fields = ['farm_name', 'location', 'crops_grown', 'buyer_type', 'contact_person', 'company_name', 'materials_accepted']
        
        for field in profile_fields:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)
        
        # Create user with only User model fields
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=password,
            role=role
        )
        
        # Create role-specific profile
        try:
            if role == 'buyer':
                buyer_profile_data = {'user': user}
                if 'buyer_type' in profile_data:
                    buyer_profile_data['buyer_type'] = profile_data['buyer_type']
                if 'company_name' in profile_data:
                    buyer_profile_data['company_name'] = profile_data['company_name']
                if 'contact_person' in profile_data:
                    buyer_profile_data['contact_person'] = profile_data['contact_person']
                
                BuyerProfile.objects.create(**buyer_profile_data)
                
            elif role == 'farmer':
                farmer_profile_data = {'user': user}
                if 'farm_name' in profile_data:
                    farmer_profile_data['farm_name'] = profile_data['farm_name']
                if 'location' in profile_data:
                    farmer_profile_data['location'] = profile_data['location']
                if 'crops_grown' in profile_data:
                    farmer_profile_data['crops_grown'] = profile_data['crops_grown']
                
                FarmerProfile.objects.create(**farmer_profile_data)
                
            elif role == 'recycler':
                recycler_profile_data = {'user': user}
                if 'company_name' in profile_data:
                    recycler_profile_data['company_name'] = profile_data['company_name']
                if 'materials_accepted' in profile_data:
                    recycler_profile_data['materials_accepted'] = profile_data['materials_accepted']
                
                RecyclerProfile.objects.create(**recycler_profile_data)
                
        except Exception as profile_error:
            # If profile creation fails, delete the user to maintain consistency
            user.delete()
            raise serializers.ValidationError(f"Profile creation failed: {str(profile_error)}")
        
        return user