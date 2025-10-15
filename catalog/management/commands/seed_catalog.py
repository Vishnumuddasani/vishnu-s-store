from django.core.management.base import BaseCommand
from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Seed initial categories and products"

    def handle(self, *args, **options):
        categories = [
            ("Electronics", "Phones, laptops, and gadgets"),
            ("Fashion", "Clothes and accessories"),
            ("Home", "Home and kitchen"),
        ]

        name_to_category = {}
        for name, _ in categories:
            category, _created = Category.objects.get_or_create(name=name)
            name_to_category[name] = category

        products = [
            ("iPhone 15", "Latest Apple iPhone", "Electronics", 999.00),
            ("Samsung Galaxy S24", "Flagship Android phone", "Electronics", 899.00),
            ("Dell XPS 13", "Ultrabook laptop", "Electronics", 1299.00),
            ("Men's Hoodie", "Comfortable cotton hoodie", "Fashion", 2499.00),
            ("Women's Sneakers", "Lightweight running shoes", "Fashion", 3999.00),
            # Men's clothing and shoes in INR
            ("Men's Shirt", "Classic fit cotton shirt", "Fashion", 1499.00),
            ("Men's Pants", "Slim fit chinos", "Fashion", 1999.00),
            ("Men's Shoes", "Leather casual shoes", "Fashion", 2999.00),
            ("Air Fryer", "Healthy frying at home", "Home", 119.00),
        ]

        created_count = 0
        for name, description, category_name, price in products:
            category = name_to_category[category_name]
            _obj, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'category': category,
                    'price': price,
                    'is_active': True,
                }
            )
            created_count += int(created)

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created {created_count} products."))


