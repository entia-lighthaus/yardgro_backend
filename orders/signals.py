from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem
from marketplace.models import Product

LOW_STOCK_THRESHOLD = 5  # example value

# Signal to reduce stock when an order item is created
# This ensures that stock is reduced immediately when an order item is saved.
@receiver(post_save, sender=OrderItem)
def reduce_stock_on_order(sender, instance, created, **kwargs):
    if created:  # new order item created
        product = instance.product
        if product.stock >= instance.quantity:
            product.stock -= instance.quantity
            product.save()

            # Suggest restock if below threshold
            if product.stock < LOW_STOCK_THRESHOLD:
                print(f"⚠️ Restock Alert: {product.name} is low on stock ({product.stock} left).")
        else:
            raise ValueError("Not enough stock available!")
