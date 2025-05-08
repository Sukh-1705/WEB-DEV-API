import os
import requests
from PIL import Image
from io import BytesIO

# List of product images to download with their direct Unsplash URLs
products = {
    'Fresh Tomatoes': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea',
    'Green Lettuce': 'https://images.unsplash.com/photo-1622205313162-be1d5712a43f',
    'Red Apples': 'https://images.unsplash.com/photo-1619546813926-a78fa6372cd2',
    'Bananas': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e',
    'Fresh Milk': 'https://images.unsplash.com/photo-1563636619-e9143da7973b',
    'Eggs': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f',
    'Sweet Oranges': 'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b',
    'Green Spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb',
    'Organic Carrots': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37',
    'Greek Yogurt': 'https://images.unsplash.com/photo-1488477181946-6428a0291777',
    'Chicken Breast': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791',
    'Fresh Bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff',
    'Coffee Beans': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e',
    'Fresh Strawberries': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6',
    'Bell Peppers': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83'
}

# Parameters to get a good size image
image_params = {
    'w': 800,
    'h': 600,
    'fit': 'crop',
    'crop': 'entropy',
    'q': 80
}

# Create directory if it doesn't exist
output_dir = 'grocery_website/store/static/img/products'
os.makedirs(output_dir, exist_ok=True)

print(f"Output directory created/verified: {output_dir}")

# Download and save images
for product_name, url in products.items():
    try:
        # Convert product name to filename
        filename = product_name.lower().replace(' ', '_') + '.jpg'
        filepath = os.path.join(output_dir, filename)
        
        print(f"\nProcessing {product_name}:")
        print(f"URL: {url}")
        print(f"Target path: {filepath}")
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"Skipping {filename} - already exists")
            continue
        
        # Download image
        print("Downloading image...")
        response = requests.get(url, params=image_params, timeout=10)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            # Open and save image
            print("Converting image...")
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            print(f"Saving to {filepath}...")
            img.save(filepath, 'JPEG', quality=85)
            print(f"Successfully downloaded {filename}")
        else:
            print(f"Failed to download {filename} - Status code: {response.status_code}")
    
    except Exception as e:
        print(f"Error downloading {product_name}: {str(e)}")
        print(f"Error type: {type(e).__name__}")

print("\nDownload process complete!") 