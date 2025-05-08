from PIL import Image
import os

# Ensure the products directory exists
os.makedirs('store/static/img/products', exist_ok=True)

# Create a basic gray image
img = Image.new('RGB', (300, 300), color=(200, 200, 200))

# Save the image
img.save('store/static/img/products/no-image.jpg')

print("Created simple placeholder image at: store/static/img/products/no-image.jpg") 