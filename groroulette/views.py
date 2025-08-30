from django.shortcuts import render
from rest_framework import generics, permissions, status
from .models import UserPreference, Spin, SpinItem, Badge, UserBadge
from orders.models import Basket, BasketItem
from .serializers import (
    SpinItemUpdateSerializer, UserPreferenceSerializer, SpinSerializer, CreateSpinSerializer,SpinItemSerializer,
    BasketSerializer, BadgeSerializer, UserBadgeSerializer
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .services import BudgetOptimizerService, BadgeService # budget optimizer and badge service for handling budget-related logic


# User Preference View
# This view allows users to retrieve and update their preferences for spins.
# It uses the UserPreferenceSerializer to handle the data.
@method_decorator(csrf_exempt, name='dispatch')
class UserPreferenceView(generics.RetrieveUpdateAPIView):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        user_pref, created = UserPreference.objects.get_or_create(user=self.request.user)
        return user_pref


# Spin List/Create View
# This view allows users to create a new spin with a budget and currency.
# It also lists existing spins for the user and manages the creation and listing of spins (the game session).
# The CreateSpinSerializer is used for creating spins, while SpinSerializer is used for listing.
# BudgetOptimizerService is used to handle the logic for generating spins based on user preferences and budget.
@method_decorator(csrf_exempt, name='dispatch')
class SpinListCreateView(generics.ListCreateAPIView):
    queryset = Spin.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        # Use CreateSpinSerializer for POST, SpinSerializer for GET
        if self.request.method == 'POST':
            return CreateSpinSerializer
        return SpinSerializer # SpinSerializer for GET requests to list spins

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use optimizer service to generate spin
        # This service will handle the logic of creating a spin based on user preferences and budget
        optimizer = BudgetOptimizerService()
        spin = optimizer.generate_spin(
            user=request.user,
            budget=serializer.validated_data['budget'],
            currency=serializer.validated_data.get('currency', 'NGN'),
            max_items=serializer.validated_data.get('max_items', 10),
            retailer_ids=serializer.validated_data.get('retailer_ids', [])
        )

        # Copy preferences snapshot on spin creation
        # This ensures that the spin has a record of the user's preferences at the time of creation
        user_pref = UserPreference.objects.get(user=request.user)
        spin.preferences = user_pref
        spin.preferences_snapshot = {
            "dietary_restrictions": user_pref.dietary_restrictions,
            "allergies": user_pref.allergies,
            "preferred_categories": user_pref.preferred_categories,
            "excluded_brands": user_pref.excluded_brands,
            "max_budget_default": str(user_pref.max_budget_default),
        }
        spin.save()

        return Response(
            SpinSerializer(spin).data,
            status=status.HTTP_201_CREATED
        )


# Spin Detail View
# This view allows users to retrieve and update the details of a specific spin.
# It uses the SpinSerializer to handle the data.
# SpinSerializer is used for both retrieving and updating spin details.
@method_decorator(csrf_exempt, name='dispatch')
class SpinDetailView(generics.RetrieveUpdateAPIView):
    queryset = Spin.objects.all()
    serializer_class = SpinSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        return Spin.objects.filter(user=self.request.user)



# Spin History View
# This view allows users to view their spin history.
# It lists all spins associated with the authenticated user.
@method_decorator(csrf_exempt, name='dispatch')
class SpinHistoryView(generics.ListAPIView):
    serializer_class = SpinSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Spin.objects.filter(user=self.request.user)
    

# Start Item Selection View
# This view allows users to start the item selection phase for a specific spin.
# It validates the spin status and allows users to select items based on the maximum number of items they can choose.
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_item_selection(request, spin_id):
    """Start the item selection phase after spin is generated"""
    spin = get_object_or_404(Spin, id=spin_id, user=request.user)
    
    if spin.status != 'generated':
        return Response(
            {'error': 'Spin must be in generated status to start selection'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    max_items_to_select = request.data.get('max_items_to_select', 5)
    
    # Validate max_items doesn't exceed generated items
    if max_items_to_select > spin.total_items_generated:
        max_items_to_select = spin.total_items_generated
    
    spin.max_items_to_select = max_items_to_select
    spin.status = 'selecting'
    spin.selection_started_at = timezone.now()
    spin.save()
    
    return Response({
        'message': f'You can now select up to {max_items_to_select} items from your spin',
        'max_items_to_select': max_items_to_select,
        'total_items_available': spin.total_items_generated
    })


# Select Spin Item View
# This view allows users to select or deselect items in their spin.
# It checks if the spin is in the correct status and whether the user can select more items
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def select_spin_item(request, spin_id, item_id):
    spin = get_object_or_404(Spin, id=spin_id, user=request.user)
    item = get_object_or_404(SpinItem, id=item_id, spin=spin)
    
    if spin.status not in ['selecting', 'completed']: 
        return Response(
            {'error': 'Selection phase has not started'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    selected = request.data.get('selected', False)
    
    if selected:
        # Check if max items limit reached
        selected_count = spin.items.filter(is_selected=True).count()
        if selected_count >= spin.max_items_to_select:
            return Response(
                {'error': f'Maximum {spin.max_items_to_select} items can be selected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item.is_selected = True
        item.selected_at = timezone.now()
    else:
        item.is_selected = False
        item.selected_at = None
    
    item.save()
    
    return Response(SpinItemSerializer(item).data)



# Complete Spin View
# This view allows users to complete their spin selection.
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def complete_spin(request, spin_id):
    spin = get_object_or_404(Spin, id=spin_id, user=request.user)
    
    if spin.status not in ['selecting', 'completed']:
        return Response(
            {'error': 'Spin must be in selecting phase to complete'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    selected_items = spin.items.filter(is_selected=True)
    
    spin.status = 'completed'
    spin.completed_at = timezone.now()
    spin.save()
    
    # Check for badges
    # This service checks if the user has earned any badges based on their spin selections
    badge_service = BadgeService()
    badges_earned = badge_service.check_badges_for_spin(spin)
    
    return Response({
        'message': 'Spin completed successfully',
        'selected_items_count': selected_items.count(),
        'max_items_allowed': spin.max_items_to_select,
        'badges_earned': badges_earned
    })




# Spin Item List View
# This view allows users to list all items in a specific spin.
# It requires authentication and returns a list of spin items for the given spin ID.
@method_decorator(csrf_exempt, name='dispatch')
class SpinItemListView(generics.ListAPIView):
    serializer_class = SpinItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        spin_id = self.kwargs.get('spin_id')
        return SpinItem.objects.filter(spin_id=spin_id)



# This view allows users to update the quantity of a specific spin item.
@method_decorator(csrf_exempt, name='dispatch')
class SpinItemUpdateView(generics.UpdateAPIView):
    queryset = SpinItem.objects.all() # update the quantity
    serializer_class = SpinItemUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Automatically recalculate the spin after updating quantity
    def perform_update(self, serializer):
        spin_item = serializer.save()
        # Automatically recalculate the spin after updating quantity
        BudgetOptimizerService().recalculate_spin(spin_item.spin)



# Spin Item Select View
# This view allows users to select a specific item in their spin.
# It updates the is_selected field of the SpinItem model.
@method_decorator(csrf_exempt, name='dispatch')
class SpinItemSelectView(APIView):
    def put(self, request, spin_id, item_id):
        try:
            item = SpinItem.objects.get(spin_id=spin_id, id=item_id)
            item.is_selected = True
            item.save()
            return Response({"selected": True}, status=status.HTTP_200_OK)
        except SpinItem.DoesNotExist:
            return Response({"error": "SpinItem not found"}, status=status.HTTP_404_NOT_FOUND)
        


# Selected Spin Item List View
# This view allows users to list all selected items in a specific spin.
@method_decorator(csrf_exempt, name='dispatch')
class SelectedSpinItemListView(generics.ListAPIView):
    serializer_class = SpinItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        spin_id = self.kwargs.get('spin_id')
        return SpinItem.objects.filter(spin_id=spin_id, is_selected=True)



# Add Selected Items to Cart View
# This view allows users to add selected items from a spin to their basket/cart.
@method_decorator(csrf_exempt, name='dispatch')
class AddSelectedItemsToBasketView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, spin_id):
        spin = get_object_or_404(Spin, id=spin_id, user=request.user)
        basket = BudgetOptimizerService().add_selected_spin_items_to_basket(spin, request.user)
        return Response({"basket_id": basket.id}, status=status.HTTP_201_CREATED)
    

# Add All Spin Items to Basket View
@method_decorator(csrf_exempt, name='dispatch')
class AddAllSpinItemsToBasketView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, spin_id):
        spin = get_object_or_404(Spin, id=spin_id, user=request.user)
        basket = BudgetOptimizerService().add_all_spin_items_to_basket(spin, request.user)
        return Response({"basket_id": basket.id}, status=status.HTTP_201_CREATED)
    


# Spin Checkout View
# This view allows users to checkout a spin and create an order.
@method_decorator(csrf_exempt, name='dispatch')
class SpinCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, spin_id):
        user = request.user
        order = BudgetOptimizerService().checkout_spin(spin_id, user)
        return Response({"order_id": order.id, "status": order.status}, status=status.HTTP_201_CREATED)
    


# Basket List/Create View
# This view allows users to create a new basket or list existing baskets.
# Manages the creation and listing of baskets (the user's selected items for purchase).
@method_decorator(csrf_exempt, name='dispatch')
class BasketListCreateView(generics.ListCreateAPIView):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]


# Badge List View
# Gamification badges are awarded based on user actions and achievements.
# This view allows users to list all available badges.
@method_decorator(csrf_exempt, name='dispatch')
class BadgeListView(generics.ListAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]


# User Badge List View
# This view allows users to list all badges they have earned.
# It filters the UserBadge model to show only badges associated with the authenticated user.
@method_decorator(csrf_exempt, name='dispatch')
class UserBadgeListView(generics.ListAPIView):
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)