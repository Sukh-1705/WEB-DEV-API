from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Sets up product images in the static directory'

    def handle(self, *args, **kwargs):
        # Define the source and destination directories
        static_dir = os.path.join(settings.BASE_DIR, 'store', 'static', 'img', 'products')
        
        # Create the directory if it doesn't exist
        os.makedirs(static_dir, exist_ok=True)
        
        # List of required product images
        required_images = [
            'cinnamon_rolls.jpg',
            'baguette.jpg',
            'chocolate_cake.jpg',
            'croissants.jpg',
            'turkey_breast.jpg',
            'pork_ribs.jpg',
            'lamb_chops.jpg',
            'ground_beef.jpg'
        ]
        
        # Check which images are missing
        missing_images = []
        for image in required_images:
            image_path = os.path.join(static_dir, image)
            if not os.path.exists(image_path):
                missing_images.append(image)
        
        if missing_images:
            self.stdout.write(self.style.WARNING(f'Missing images: {", ".join(missing_images)}'))
            self.stdout.write(self.style.WARNING('Please add these images to the static/img/products directory'))
        else:
            self.stdout.write(self.style.SUCCESS('All required product images are present')) 