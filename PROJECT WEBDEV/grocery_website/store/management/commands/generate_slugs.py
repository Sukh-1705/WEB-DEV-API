from django.core.management.base import BaseCommand
from store.models import Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Generate slugs for products that do not have them'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            if not product.slug:
                base_slug = slugify(product.name)
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                product.slug = slug
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Generated slug for product {product.name}: {slug}')) 