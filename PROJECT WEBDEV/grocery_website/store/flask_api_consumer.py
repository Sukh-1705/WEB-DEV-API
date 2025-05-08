from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import json
from .models import Cart, CartItem, Product
from .api_client import FlaskAPIClient
import logging

logger = logging.getLogger(__name__)

def get_or_create_cart(request):
    """Helper function to get or create a cart for the user"""
    from .views import get_or_create_cart as existing_get_or_create_cart
    return existing_get_or_create_cart(request)

def get_product_image_url(product_name):
    """Helper function to get image URL based on product name"""
    # Try most common image extensions
    for ext in ['jpg', 'png', 'jpeg', 'gif', 'jfif']:
        # Check with exact filename match
        image_url = f"http://127.0.0.1:5000/static/images/{product_name}.{ext}"
        return image_url  # Return the first matched extension
    
    # If no match, return a generic image
    return "http://127.0.0.1:5000/static/images/placeholder.jpg"

@csrf_protect
@require_POST
def add_flask_product_to_cart(request):
    """
    Add a product from Flask API to the Django cart
    
    This function handles AJAX requests to add Flask API products to the cart
    """
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        price = float(data.get('price', 0))
        image_url = data.get('image_url', '')
        quantity = int(data.get('quantity', 1))
        
        if not all([product_id, product_name, price]):
            return JsonResponse({"success": False, "error": "Missing required fields"})
        
        # Use product name to determine image URL
        if product_name:
            image_url = get_product_image_url(product_name)
        
        # Get the user's cart
        cart = get_or_create_cart(request)
        
        # Check if we already have a local product for this Flask product
        flask_product_id = f"flask_{product_id}"
        product = Product.objects.filter(name=product_name).first()
        
        if not product:
            # Create a temporary local product representation
            category = None  # Optional: get or create a category from Flask API
            
            # Create a new product entry in Django DB
            product = Product.objects.create(
                name=product_name,
                price=price,
                # Use the Flask product ID as external ID or in the slug
                slug=flask_product_id,
                is_available=True,
                # If you have a field to store external source info:
                # source='flask_api',
                # external_id=product_id
            )
            
            logger.info(f"Created local product reference for Flask product: {product_name}")
        
        # Check if this product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )
        
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        
        cart_item.save()
        
        # Also add to Flask cart if the user is authenticated
        if request.user.is_authenticated:
            try:
                # Get Flask user ID (if there's a mapping between Django and Flask users)
                # flask_user_id = get_flask_user_id(request.user)
                # For demo, let's just use Django user ID
                flask_user_id = request.user.id
                
                flask_cart_data = {
                    'user_id': flask_user_id,
                    'product_name': product_name,
                    'price': price,
                    'image_url': image_url
                }
                
                # Add to Flask cart using API
                FlaskAPIClient.add_to_cart(flask_cart_data)
                logger.info(f"Added product to Flask cart: {product_name}")
            except Exception as e:
                logger.error(f"Error adding to Flask cart: {str(e)}")
        
        # Get updated cart count
        cart_count = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
        
        return JsonResponse({
            "success": True,
            "message": f"{product_name} added to cart",
            "cart_count": cart_count
        })
        
    except Exception as e:
        logger.error(f"Error in add_flask_product_to_cart: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}) 