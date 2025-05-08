import os
import django
import re
from django.core.files import File

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grocery_website.settings')
django.setup()

# Import the Product model after setting up Django
from store.models import Product

def normalize_name(name):
    """Convert product name to a format that might match filenames"""
    # Convert to lowercase, replace spaces with underscores
    normalized = name.lower().replace(' ', '_')
    # Remove non-alphanumeric characters (except underscores)
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)
    return normalized

def main():
    # Path to static images directory
    static_img_dir = 'store/static/img/products'
    
    # Get list of all images in the directory
    available_images = {}
    for filename in os.listdir(static_img_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Store filename without extension as key
            name, ext = os.path.splitext(filename)
            available_images[name.lower()] = filename
    
    # Get all products
    products = Product.objects.all()
    print(f"Found {len(products)} products and {len(available_images)} images")
    
    update_count = 0
    for product in products:
        # Skip products that already have images
        if product.image and product.image.name:
            print(f"Product '{product.name}' already has image: {product.image.name}")
            continue
        
        # Try to find matching image by product name
        product_key = normalize_name(product.name)
        
        if product_key in available_images:
            # Found exact match
            image_file = available_images[product_key]
            update_product_image(product, image_file, static_img_dir)
            update_count += 1
        else:
            # Try partial match
            matched = False
            for img_key, img_file in available_images.items():
                if product_key in img_key or img_key in product_key:
                    update_product_image(product, img_file, static_img_dir)
                    update_count += 1
                    matched = True
                    break
            
            if not matched:
                print(f"No matching image found for '{product.name}'")
    
    print(f"Updated {update_count} products with images")

def update_product_image(product, image_filename, static_img_dir):
    """Update product with image from static directory"""
    image_path = os.path.join(static_img_dir, image_filename)
    
    # Copy image to media directory through Django's File model
    with open(image_path, 'rb') as img_file:
        # Set the image field (this will copy to MEDIA_ROOT/products/)
        product.image.save(
            f"products/{image_filename}",  # Path within media directory
            File(img_file),
            save=True
        )
    
    print(f"Updated product '{product.name}' with image: {image_filename}")

if __name__ == "__main__":
    main() 