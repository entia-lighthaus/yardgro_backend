from itertools import product
from .models import Spin, SpinItem, Badge, UserBadge, Product, UserPreference
from orders.models import Basket, Order, OrderItem, BasketItem
from django.utils import timezone


# Budget Optimizer Service
# Handles logic for generating a spin based on user budget, preferences, and other constraints.
class BudgetOptimizerService:
   
    def generate_spin(self, user, budget, currency='NGN', max_items=10, retailer_ids=None):
        user_pref, created = UserPreference.objects.get_or_create(user=user) 

        products = Product.objects.filter(price__lte=budget)

        if not budget:
            budget = user_pref.max_budget_default or 0    # Use budget from request if provided, else fallback to user_pref
        # To Filter spins by preferred categories if set
        if user_pref.preferred_categories:
            products = products.filter(category__pk__in=user_pref.preferred_categories)
        products = products.order_by('-price')  # Start with most expensive

        selected_items = []
        total = 0

        # A simple greedy algorithm to select items until budget or max_items is reached
        for product in products:
            if len(selected_items) >= max_items:
                break
            max_quantity = int((budget - total) // product.price)
            if max_quantity > 0:
                quantity = min(max_quantity, 10)  # flexible: You can set a sensible max per item
                selected_items.append((product, quantity))
                total += product.price * quantity

   

        spin = Spin.objects.create(
            user=user,
            budget=budget,
            currency=currency,
            total_items_generated=len(selected_items),
            total_value=total,
            max_items_to_select=max_items,
            status='generated',
            created_at=timezone.now()
        )
       
        for idx, (product, quantity) in enumerate(selected_items):
            SpinItem.objects.create(
                spin=spin,
                product=product,
                name=product.name,
                price=product.price,
                price_unit=product.price_unit,
                unit_price=product.price,
                quantity=quantity,
                position_in_spin=idx + 1,
                is_selected=False
            )
        return spin
    

    # Recalculate spin items based on remaining budget
    def recalculate_spin(self, spin):
        user_pref = spin.preferences
        budget = spin.budget
        used_value = sum(item.unit_price * item.quantity for item in spin.items.all())
        remaining_budget = budget - used_value

        # To select new products to fill the remaining budget
        products = Product.objects.filter(
            price__lte=remaining_budget,
            category__pk__in=user_pref.preferred_categories
        ).exclude(id__in=[item.product.id for item in spin.items.all()])

        products = products.order_by('-price')

        for product in products:
            if remaining_budget < product.price:
                continue
            max_quantity = int(remaining_budget // product.price)
            if max_quantity > 0:
                SpinItem.objects.create(
                    spin=spin,
                    product=product,
                    name=product.name,
                    price=product.price,
                    price_unit=product.price_unit,
                    unit_price=product.price,
                    quantity=max_quantity,
                    position_in_spin=spin.items.count() + 1,
                    is_selected=False
                )
                remaining_budget -= product.price * max_quantity

        # Update spin total value and items count
        spin.total_value = sum(item.unit_price * item.quantity for item in spin.items.all())
        spin.total_items_generated = spin.items.count()
        spin.save()


    # Add selected items from a spin to the user's basket/cart
    def add_selected_spin_items_to_basket(self, spin, user):
        basket, _ = Basket.objects.get_or_create(user=user)
        selected_items = spin.items.filter(is_selected=True)
        for idx, item in enumerate(selected_items):
            BasketItem.objects.create(
                basket=basket,
                product=item.product,
                quantity=item.quantity,
                price=item.unit_price,
                name=item.name,
                position_in_spin=idx + 1
            )
        return basket
    
    # add all spin items to basket
    def add_all_spin_items_to_basket(self, spin, user):
        basket, _ = Basket.objects.get_or_create(user=user)
        all_items = spin.items.all()
        for idx, item in enumerate(all_items):
            BasketItem.objects.create(
                basket=basket,
                product=item.product,
                quantity=item.quantity,
                price=item.unit_price,
                name=item.name,
                position_in_spin=idx + 1
            )
        return basket


    
    # Add a specific marketplace product to the user's basket/cart
    def add_marketplace_item_to_basket(self, product, quantity, user):
        basket, _ = Basket.objects.get_or_create(user=user)
        BasketItem.objects.create(
            basket=basket,
            product=product,
            quantity=quantity,
            price=product.price,
            name=product.name,
            position_in_spin=basket.items.count() + 1
        )
        return basket

    
    
 

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