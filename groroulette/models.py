from django.db import models
from django.conf import settings
import uuid
from marketplace.models import Product



# User Preference Model
# Stores user preferences for dietary restrictions, allergies, preferred categories, etc
# This model is linked to the User model with a one to one relationship and allows for customization of the roulette spin.
class UserPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    dietary_restrictions = models.JSONField(default=list)  # ["vegetarian", "gluten_free"]
    allergies = models.JSONField(default=list)
    preferred_categories = models.JSONField(default=list)
    excluded_brands = models.JSONField(default=list)
    max_budget_default = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_preferences'




# Spin Model
# Each Spin represents a user's attempt to generate a roulette of products based on their preferences and budget.
# The Spin model tracks the user, budget, preferences, and whether the spin is completed.
class Spin(models.Model):
    STATUS_CHOICES = [
        ('generated', 'Generated'),  # Spin created, items generated
        ('selecting', 'Selecting'),  # User is selecting items
        ('completed', 'Completed'),  # User completed selection
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spins')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    total_items_generated = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_items_to_select = models.PositiveIntegerField(default=5)
    preferences = models.ForeignKey(UserPreference, on_delete=models.SET_NULL, null=True, blank=True)
    preferences_snapshot = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated')
    selection_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spins'
        ordering = ['-created_at']

    def __str__(self):
        return f"Spin {self.id} - {self.user.username} - {self.budget} {self.currency}"




# Spin Item Model
# Represents an item selected in a Spin, linking to a product in the marketplace.
# This model allows for multiple items to be selected in a single spin.
# The details field can store additional product information (e.g., description, nutrition, images).
# The product_id can be used to link or search for the product in the marketplace app for full details.
class SpinItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spin = models.ForeignKey(Spin, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # Reference to product in marketplace app
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=50, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    position_in_spin = models.IntegerField()  # Order in roulette result
    is_selected = models.BooleanField(default=False)
    selected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'spin_items'
        ordering = ['position_in_spin']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)




# Basket Model
# Represents a user's shopping basket, which can contain multiple SpinItems.
# This model allows users to save their selected items from a Spin for later checkout.
# It can also be linked to a Spin for context.
# The checked_out field indicates whether the basket has been processed for checkout.
class Basket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='baskets')
    spin = models.ForeignKey(Spin, on_delete=models.CASCADE, related_name='basket', null=True, blank=True)
    items = models.ManyToManyField(SpinItem)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)



# Badge Model
# Represents a badge that can be awarded to users based on their spins or achievements.
# This model allows for gamification of the user experience, rewarding users for participation.
# The badge can have different types and attributes like title, description, icon, and points.
class Badge(models.Model):
    BADGE_TYPES = [
        ('smart_shopper', 'Smart Shopper'),
        ('budget_master', 'Budget Master'),
        ('variety_explorer', 'Variety Explorer'),
        ('loyal_customer', 'Loyal Customer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=BADGE_TYPES, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', blank=True)
    points = models.IntegerField(default=10)

    class Meta:
        db_table = 'badges'


# UserBadge Model
# Links a user to a badge, allowing for tracking of which badges a user has earned.
# The spin field can link to a specific Spin that earned the badge, if applicable.
class UserBadge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    name = models.CharField(max_length=100)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    spin = models.ForeignKey(Spin, on_delete=models.CASCADE, null=True, blank=True)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge', 'spin']
        db_table = 'user_badges'