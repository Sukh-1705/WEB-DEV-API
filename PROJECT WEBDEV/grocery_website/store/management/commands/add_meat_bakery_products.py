from django.core.management.base import BaseCommand
from store.models import Category, Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Adds meat and bakery products to the database'

    def handle(self, *args, **kwargs):
        # Create meat category if it doesn't exist
        meat_category, _ = Category.objects.get_or_create(
            type='meat',
            defaults={
                'name': 'Meat & Poultry',
                'slug': 'meat-poultry'
            }
        )

        # Create bakery category if it doesn't exist
        bakery_category, _ = Category.objects.get_or_create(
            type='bakery',
            defaults={
                'name': 'Bakery & Bread',
                'slug': 'bakery-bread'
            }
        )

        # Meat products
        meat_products = [
            {
                'name': 'Chicken Breast',
                'description': 'Fresh, boneless chicken breast. Perfect for grilling or baking.',
                'price': 299.99,
                'quantity': '500g',
                'discount': 10,
                'category': meat_category
            },
            {
                'name': 'Ground Beef',
                'description': 'Premium quality ground beef. Great for burgers and meatballs.',
                'price': 399.99,
                'quantity': '500g',
                'discount': 5,
                'category': meat_category
            },
            {
                'name': 'Lamb Chops',
                'description': 'Tender lamb chops. Perfect for special occasions.',
                'price': 699.99,
                'quantity': '500g',
                'discount': 0,
                'category': meat_category
            },
            {
                'name': 'Pork Ribs',
                'description': 'Meaty pork ribs. Ideal for BBQ and slow cooking.',
                'price': 449.99,
                'quantity': '1kg',
                'discount': 15,
                'category': meat_category
            },
            {
                'name': 'Turkey Breast',
                'description': 'Lean turkey breast. Great for sandwiches and salads.',
                'price': 349.99,
                'quantity': '500g',
                'discount': 0,
                'category': meat_category
            }
        ]

        # Bakery products
        bakery_products = [
            {
                'name': 'Fresh Bread',
                'description': 'Artisanal whole wheat bread. Baked fresh daily.',
                'price': 49.99,
                'quantity': '400g',
                'discount': 0,
                'category': bakery_category
            },
            {
                'name': 'Croissants',
                'description': 'Buttery, flaky croissants. Perfect for breakfast.',
                'price': 39.99,
                'quantity': '4 pieces',
                'discount': 10,
                'category': bakery_category
            },
            {
                'name': 'Chocolate Cake',
                'description': 'Rich chocolate cake with ganache frosting.',
                'price': 299.99,
                'quantity': '500g',
                'discount': 5,
                'category': bakery_category
            },
            {
                'name': 'Baguette',
                'description': 'Crispy French baguette. Perfect for sandwiches.',
                'price': 59.99,
                'quantity': '250g',
                'discount': 0,
                'category': bakery_category
            },
            {
                'name': 'Cinnamon Rolls',
                'description': 'Sweet cinnamon rolls with cream cheese frosting.',
                'price': 79.99,
                'quantity': '4 pieces',
                'discount': 15,
                'category': bakery_category
            }
        ]

        # Add all products
        all_products = meat_products + bakery_products
        
        for product_data in all_products:
            # Generate slug from name
            slug = slugify(product_data['name'])
            
            # Create or update product
            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': product_data['name'],
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'quantity': product_data['quantity'],
                    'discount': product_data['discount'],
                    'category': product_data['category'],
                    'is_available': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created product "{product.name}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully updated product "{product.name}"')) 