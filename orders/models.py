from django.db import models
from django.conf import settings
from marketplace.models import Product

User = settings.AUTH_USER_MODEL


# Order Model
# Represents a user's order, which can contain multiple products.
# Each order has a status and is linked to a user.
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_baskets")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')

    def __str__(self):
        return f"Order {self.id} by {self.user}"


# Order Item Model
# Represents an item in an order, linking to a specific product and quantity.
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# Basket Model
# Represents a user's shopping basket, which can contain multiple products before finalizing an order.
class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="baskets")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Basket {self.id} for {self.user}"

# Basket Item Model
# Represents an item in a user's shopping basket, linking to a specific product and quantity.
class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)
    position_in_spin = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Basket {self.basket.id}"