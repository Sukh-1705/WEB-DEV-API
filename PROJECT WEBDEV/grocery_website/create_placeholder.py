from PIL import Image, ImageDraw, ImageFont
import os

# Create a white background image
img = Image.new('RGB', (300, 300), color=(240, 240, 240))
draw = ImageDraw.Draw(img)

# Draw a gray border
draw.rectangle([(10, 10), (290, 290)], outline=(200, 200, 200), width=2)

# Add text (if PIL has default fonts)
try:
    # Try to add text - may not work depending on font availability
    font = ImageFont.load_default()
    draw.text((75, 140), "No Image Available", fill=(100, 100, 100), font=font)
except Exception:
    # If text doesn't work, draw a symbol
    draw.line([(50, 50), (250, 250)], fill=(200, 200, 200), width=5)
    draw.line([(250, 50), (50, 250)], fill=(200, 200, 200), width=5)

# Ensure the products directory exists
os.makedirs('store/static/img/products', exist_ok=True)

# Save the image
img.save('store/static/img/products/no-image.jpg')

print("Placeholder image created at: store/static/img/products/no-image.jpg") 