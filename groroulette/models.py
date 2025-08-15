from django.db import models
from django.conf import settings
import uuid

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spins')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    preferences = models.ForeignKey(UserPreference, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    max_selectable_items = models.PositiveIntegerField(default=5)
    is_completed = models.BooleanField(default=False)



# Spin Item Model
# Represents an item selected in a Spin, linking to a product in the marketplace.
# This model allows for multiple items to be selected in a single spin.
# The details field can store additional product information (e.g., description, nutrition, images).
# The product_id can be used to link or search for the product in the marketplace app for full details.
class SpinItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spin = models.ForeignKey(Spin, on_delete=models.CASCADE, related_name='items')
    product_id = models.UUIDField()  # Reference to product in marketplace app
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.JSONField(default=dict)  # Store extra product info



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
# The spin field can link to a specific Spin that earned the badge, if applicable.
class Badge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    name = models.CharField(max_length=100)
    description = models.TextField()
    earned_at = models.DateTimeField(auto_now_add=True)
    spin = models.ForeignKey(Spin, on_delete=models.SET_NULL, null=True, blank=True)