from .models import Spin, SpinItem, Badge, UserBadge
from django.utils import timezone


# Budget Optimizer Service
# Handles logic for generating a spin based on user budget, preferences, and other constraints.
class BudgetOptimizerService:
   
    def generate_spin(self, user, budget, currency='NGN', max_items=10, retailer_ids=None):
        # 1. Fetch user preferences
        user_pref = getattr(user, 'preferences', None)
        # 2. Query products from marketplace based on preferences, budget, etc.
        # 3. Select optimal products for the spin
        # 4. Create Spin and SpinItem objects
        spin = Spin.objects.create(
            user=user,
            budget=budget,
            currency=currency,
            status='generated',
            max_items_to_select=max_items,
            total_items_generated=max_items,  # Example, adjust as needed
            created_at=timezone.now()
        )
        # Example: create dummy SpinItems (replace with real product selection logic)
        for i in range(max_items):
            SpinItem.objects.create(
                spin=spin,
                name=f"Product {i+1}",
                price=budget / max_items,
                is_selected=False
            )
        return spin


# Badge Service
# Handles logic for awarding badges based on user actions and achievements.
class BadgeService:
    """
    Handles logic for awarding badges based on user actions and achievements.
    """
    def check_badges_for_spin(self, spin):
        badges_earned = []
        # Example logic: award "Smart Shopper" badge if all items are selected
        if spin.items.filter(is_selected=True).count() == spin.max_items_to_select:
            badge, created = Badge.objects.get_or_create(
                name="Smart Shopper",
                defaults={"description": "Collected all items from a spin!"}
            )
            UserBadge.objects.get_or_create(user=spin.user, badge=badge, spin=spin)
            badges_earned.append(badge.name)
        # Add more badge logic as needed
        return badges_earned