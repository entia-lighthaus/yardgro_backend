from django.shortcuts import render
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductRating
from .serializers import CategorySerializer, ProductSerializer, ProductRatingSerializer

# Category Views
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# Product Views
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    # Enable search & filter by name and category
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    ordering = ['id'] 

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# Rating Views
class ProductRatingCreateUpdateAPIView(generics.CreateAPIView):
    serializer_class = ProductRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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


    