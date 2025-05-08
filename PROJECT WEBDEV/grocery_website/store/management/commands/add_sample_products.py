from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Add sample products to the database'

    def handle(self, *args, **kwargs):
        # First, clear existing data
        Category.objects.all().delete()
        Product.objects.all().delete()

        # Create categories first
        categories = {
            'fruits': Category.objects.create(name='Fruits', type='fruits'),
            'vegetables': Category.objects.create(name='Vegetables', type='vegetables'),
            'dairy': Category.objects.create(name='Dairy', type='dairy'),
            'meat': Category.objects.create(name='Meat', type='meat'),
            'bakery': Category.objects.create(name='Bakery', type='bakery'),
        }

        # Sample products data - names exactly matching image filenames (without .jpg)
        products = [
            {
                'name': 'Fresh Tomatoes',
                'category': categories['vegetables'],
                'price': 4.99,
                'description': 'Fresh, ripe tomatoes perfect for salads and cooking.',
                'is_available': True
            },
            {
                'name': 'Green Lettuce',
                'category': categories['vegetables'],
                'price': 2.99,
                'description': 'Crisp and fresh green lettuce.',
                'is_available': True
            },
            {
                'name': 'Red Apples',
                'category': categories['fruits'],
                'price': 5.99,
                'description': 'Sweet and juicy red apples.',
                'is_available': True
            },
            {
                'name': 'Bananas',
                'category': categories['fruits'],
                'price': 3.99,
                'description': 'Fresh yellow bananas.',
                'is_available': True
            },
            {
                'name': 'Fresh Milk',
                'category': categories['dairy'],
                'price': 2.99,
                'description': 'Fresh whole milk.',
                'is_available': True
            },
            {
                'name': 'Eggs',
                'category': categories['dairy'],
                'price': 4.99,
                'description': 'Farm fresh eggs.',
                'is_available': True
            },
            {
                'name': 'Sweet Oranges',
                'category': categories['fruits'],
                'price': 5.99,
                'description': 'Sweet and juicy oranges.',
                'is_available': True
            },
            {
                'name': 'Green Spinach',
                'category': categories['vegetables'],
                'price': 2.99,
                'description': 'Fresh green spinach leaves.',
                'is_available': True
            },
            {
                'name': 'Organic Carrots',
                'category': categories['vegetables'],
                'price': 2.49,
                'description': 'Organic fresh carrots.',
                'is_available': True
            },
            {
                'name': 'Greek Yogurt',
                'category': categories['dairy'],
                'price': 4.99,
                'description': 'Creamy Greek yogurt.',
                'is_available': True
            }
        ]

        # Create products
        for product_data in products:
            Product.objects.create(**product_data)

        self.stdout.write(self.style.SUCCESS('Successfully added sample products')) 