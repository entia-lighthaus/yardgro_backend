from rest_framework import serializers
from .models import Order, OrderItem
from marketplace.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # ✅ expects product ID

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']  # ✅ this will be a Product instance now
            quantity = item_data['quantity']

            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.stock}"
                )

            # Reduce stock
            product.stock -= quantity
            product.save()

            # Create order item
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order





    def save(self, *args, **kwargs):
        """Reduce stock automatically when an order item is saved."""
        if not self.pk:  # only reduce stock when creating
            if self.product.quantity < self.quantity:
                raise ValueError("Not enough stock available")
            self.product.quantity -= self.quantity
            self.product.save()

        super().save(*args, **kwargs)



tests
{
  "items": [
    {"product": 1, "quantity": 2},
    {"product": 3, "quantity": 1}
  ]
}

# 1. Fetch user preferences
        user_pref = getattr(user, 'preferences', None)
        # 2. Query products from marketplace based on preferences, budget, etc.
        # 3. Select optimal products for the spin
        # 4. Create Spin and SpinItem objects