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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user}"


# Order Item Model
# Represents an item in an order, linking to a specific product and quantity.
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs):
        """Reduce stock automatically when an order item is saved."""
        if not self.pk:  # only reduce stock when creating
            if self.product.quantity < self.quantity:
                raise ValueError("Not enough stock available")
            self.product.quantity -= self.quantity
            self.product.save()

        super().save(*args, **kwargs)
