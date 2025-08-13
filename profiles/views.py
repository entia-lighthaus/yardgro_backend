
from rest_framework import generics, permissions
from .models import FarmerProfile, BuyerProfile, RecyclerProfile
from .serializers import (
	FarmerProfileUpdateSerializer,
	BuyerProfileUpdateSerializer,
	RecyclerProfileUpdateSerializer
)

# List all profiles (can be customized to filter by type)
class ProfileListView(generics.ListAPIView):
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		# Combine all profiles into one queryset (can be customized)
		return list(FarmerProfile.objects.all()) + list(BuyerProfile.objects.all()) + list(RecyclerProfile.objects.all())

	def list(self, request, *args, **kwargs):
		# Custom list to show all profiles
		farmers = FarmerProfileUpdateSerializer(FarmerProfile.objects.all(), many=True).data
		buyers = BuyerProfileUpdateSerializer(BuyerProfile.objects.all(), many=True).data
		recyclers = RecyclerProfileUpdateSerializer(RecyclerProfile.objects.all(), many=True).data
		return generics.Response({
			'farmers': farmers,
			'buyers': buyers,
			'recyclers': recyclers
		})

# Detail view for a single profile (by pk and type)
class ProfileDetailView(generics.RetrieveUpdateAPIView):
	permission_classes = [permissions.IsAuthenticated]

	def get_serializer_class(self):
		profile_type = self.kwargs.get('type')
		if profile_type == 'farmer':
			return FarmerProfileUpdateSerializer
		elif profile_type == 'buyer':
			return BuyerProfileUpdateSerializer
		elif profile_type == 'recycler':
			return RecyclerProfileUpdateSerializer
		else:
			raise Exception('Invalid profile type')

	def get_queryset(self):
		profile_type = self.kwargs.get('type')
		if profile_type == 'farmer':
			return FarmerProfile.objects.all()
		elif profile_type == 'buyer':
			return BuyerProfile.objects.all()
		elif profile_type == 'recycler':
			return RecyclerProfile.objects.all()
		else:
			raise Exception('Invalid profile type')
