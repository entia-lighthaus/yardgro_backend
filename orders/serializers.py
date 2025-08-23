from rest_framework import serializers
from .models import Order, OrderItem
from marketplace.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']



# Serializer for Orders
# This serializer handles the representation of an entire order, including its items.
# It includes validation for the order items and their quantities.
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'items']
        read_only_fields = ['user', 'status', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        validated_data.pop('user', None)
        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product_id = item_data['product']  # assign first!
            quantity = item_data['quantity']

            # fetch product from DB
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with id {product_id} does not exist.")

            # check stock availability
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for product '{product.name}'. "
                    f"Requested: {quantity}, Available: {product.stock}"
                )

            # to reduce stock
            product.stock -= quantity
            product.save()

            # create order item
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order


