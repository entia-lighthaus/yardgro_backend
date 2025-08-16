from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from groroulette.models import UserPreference, Spin, SpinItem, Basket, Badge, UserBadge
from apps.products.models import Product, Category
from decimal import Decimal
import random
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with test data for GroRoulette'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of test users to create')
        parser.add_argument('--spins', type=int, default=10, help='Number of spins to create per user')
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            SpinItem.objects.all().delete()
            Spin.objects.all().delete()
            UserPreference.objects.all().delete()
            Basket.objects.all().delete()
            Badge.objects.all().delete()
            UserBadge.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.create_badges()
        self.create_users_with_preferences(options['users'])
        self.create_spins_and_items(options['spins'])
        self.stdout.write(self.style.SUCCESS('Successfully seeded GroRoulette test data!'))

    def create_badges(self):
        badge_types = [
            ('smart_shopper', 'Smart Shopper', 'Collected all items from a spin!', 10),
            ('budget_master', 'Budget Master', 'Optimized your budget perfectly!', 15),
            ('variety_explorer', 'Variety Explorer', 'Selected items from multiple categories!', 12),
            ('loyal_customer', 'Loyal Customer', 'Played GroRoulette many times!', 20),
        ]
        for name, title, desc, points in badge_types:
            Badge.objects.get_or_create(
                name=name,
                defaults={'title': title, 'description': desc, 'points': points}
            )

    def create_users_with_preferences(self, num_users):
        dietary_options = [[], ['vegetarian'], ['gluten_free'], ['dairy_free']]
        allergies_options = [[], ['nuts'], ['shellfish'], ['dairy']]
        categories = list(Category.objects.values_list('name', flat=True))

        for i in range(num_users):
            username = f'testuser{i+1}'
            email = f'testuser{i+1}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
                defaults={'password': 'pbkdf2_sha256$260000$test123'}  # password: test123
            )
            if created:
                UserPreference.objects.get_or_create(
                    user=user,
                    defaults={
                        'dietary_restrictions': random.choice(dietary_options),
                        'allergies': random.choice(allergies_options),
                        'preferred_categories': random.sample(categories, k=min(3, len(categories))),
                        'excluded_brands': [],
                        'max_budget_default': Decimal(str(random.randint(10000, 100000)))
                    }
                )
                self.stdout.write(f'Created user: {username} with preferences')

    def create_spins_and_items(self, spins_per_user):
        users = User.objects.filter(is_superuser=False)
        products = list(Product.objects.all())
        for user in users:
            user_pref = getattr(user, 'preferences', None)
            for s in range(spins_per_user):
                budget = user_pref.max_budget_default if user_pref else Decimal('50000')
                spin = Spin.objects.create(
                    user=user,
                    budget=budget,
                    currency='NGN',
                    max_items_to_select=5,
                    preferences=user_pref,
                    preferences_snapshot={
                        'dietary_restrictions': user_pref.dietary_restrictions if user_pref else [],
                        'allergies': user_pref.allergies if user_pref else [],
                        'preferred_categories': user_pref.preferred_categories if user_pref else [],
                        'excluded_brands': user_pref.excluded_brands if user_pref else [],
                        'max_budget_default': str(budget)
                    },
                    status='generated'
                )
                selected_products = random.sample(products, k=min(5, len(products)))
                for idx, product in enumerate(selected_products):
                    SpinItem.objects.create(
                        spin=spin,
                        product_id=product.id,
                        name=product.name,
                        price=Decimal(str(random.randint(500, 5000))),
                        quantity=1,
                        position_in_spin=idx+1,
                        is_selected=False
                    )
                spin.total_items_generated = len(selected_products)
                spin.total_value = sum([item.price for item in spin.items.all()])
                spin.save()
                self.stdout.write(f'Created spin for user {user.username} with {len(selected_products)} items')