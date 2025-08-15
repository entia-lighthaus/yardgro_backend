from django.shortcuts import render
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Category, Product, ProductRating, Favorite
from .serializers import CategorySerializer, ProductSerializer, ProductRatingSerializer, FavoriteSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



# Category Views
@method_decorator(csrf_exempt, name='dispatch')
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]


# Product Views
@method_decorator(csrf_exempt, name='dispatch')
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]

    # Enable search & filter by name and category
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    ordering = ['id'] # this enables ordering to display from 1-20.. not in reverse, 20 - 1

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]


# Rating Views
@method_decorator(csrf_exempt, name='dispatch')
class ProductRatingCreateUpdateAPIView(generics.CreateAPIView):
    serializer_class = ProductRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def create(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product')  # Changed from 'product_id' to 'product'
        
        if not product_id:
            return Response({"detail": "product is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # This is to Check if rating exists for this user and product
        rating_obj = ProductRating.objects.filter(product=product, user=user).first()
        
        # Prepare data without user field (it's read-only in serializer)
        data = {
            "product": product.id,
            "rating": request.data.get('rating'),
            "review": request.data.get('review', ''),
        }
        
        if rating_obj:
            # Update existing rating
            serializer = self.get_serializer(rating_obj, data=data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new rating
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()  # The user will be set automatically in the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)




# Favorite Views
# List all favorites for the authenticated user

@method_decorator(csrf_exempt, name='dispatch')
class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    

@method_decorator(csrf_exempt, name='dispatch')
class FavoriteCreateView(generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
