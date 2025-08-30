from django.shortcuts import render
from .models import Order
from rest_framework import generics, permissions, status
from .serializers import OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.models import Basket, Order, OrderItem

# View for listing and creating orders
# This view allows authenticated users to list their orders and create new ones.
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



# View for retrieving a single order
# This view allows authenticated users to retrieve details of a specific order.
class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)




# View for checking out a basket and creating an order
class BasketCheckoutView(APIView):
    def post(self, request, basket_id):
        basket = Basket.objects.get(id=basket_id, user=request.user)
        order = Order.objects.create(user=request.user, status='completed')
        for item in basket.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            )
        basket.items.all().delete()  # Optionally clear basket
        return Response({"order_id": order.id, "status": order.status}, status=status.HTTP_201_CREATED)