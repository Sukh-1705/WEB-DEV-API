import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Flask API base URL - update this to your Flask server URL
FLASK_API_BASE_URL = 'http://127.0.0.1:5000/api'

class FlaskAPIClient:
    """
    Client for interacting with the Flask REST API
    """
    @staticmethod
    def get_headers():
        """Return default headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    @staticmethod
    def make_request(method, endpoint, data=None, params=None):
        """
        Make a request to the Flask API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            data (dict, optional): Request data for POST/PUT requests
            params (dict, optional): URL parameters for GET requests
            
        Returns:
            dict: Response data or error information
        """
        url = f"{FLASK_API_BASE_URL}/{endpoint}"
        headers = FlaskAPIClient.get_headers()
        
        logger.info(f"Making {method} request to {url}")
        if data:
            logger.info(f"Request data: {data}")
        if params:
            logger.info(f"Request params: {params}")
            
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data))
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data))
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return {'error': 'Invalid HTTP method'}
            
            logger.info(f"Response status code: {response.status_code}")
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Return JSON response if available
            if response.content:
                result = response.json()
                logger.info(f"Response data: {result}")
                return result
            return {'status': 'success'}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return {'error': str(e)}
    
    # User API methods
    @classmethod
    def get_users(cls):
        """Get all users from Flask API"""
        return cls.make_request('GET', 'users')
    
    @classmethod
    def get_user(cls, user_id):
        """Get a specific user by ID"""
        return cls.make_request('GET', f'users/{user_id}')
    
    @classmethod
    def create_user(cls, user_data):
        """Create a new user in Flask"""
        return cls.make_request('POST', 'users', data=user_data)
    
    # Product API methods
    @classmethod
    def get_products(cls):
        """Get all products from Flask API"""
        result = cls.make_request('GET', 'products')
        
        # Process image URLs if necessary
        if isinstance(result, list):
            for product in result:
                if product.get('image_url'):
                    logger.info(f"Product {product.get('name')} has image URL: {product.get('image_url')}")
                else:
                    logger.warning(f"Product {product.get('name')} has no image URL")
        
        return result
    
    @classmethod
    def get_product(cls, product_id):
        """Get a specific product by ID"""
        result = cls.make_request('GET', f'products/{product_id}')
        
        # Log image URL for debugging
        if isinstance(result, dict) and not 'error' in result:
            if result.get('image_url'):
                logger.info(f"Product {result.get('name')} has image URL: {result.get('image_url')}")
            else:
                logger.warning(f"Product {result.get('name')} has no image URL")
        
        return result
    
    @classmethod
    def create_product(cls, product_data):
        """Create a new product in Flask"""
        return cls.make_request('POST', 'products', data=product_data)
    
    # Category API methods
    @classmethod
    def get_categories(cls):
        """Get all categories from Flask API"""
        return cls.make_request('GET', 'categories')
    
    @classmethod
    def get_category(cls, category_id):
        """Get a specific category by ID"""
        return cls.make_request('GET', f'categories/{category_id}')
    
    @classmethod
    def create_category(cls, category_data):
        """Create a new category in Flask"""
        return cls.make_request('POST', 'categories', data=category_data)
    
    # Cart API methods
    @classmethod
    def get_cart(cls, user_id):
        """Get a user's cart"""
        return cls.make_request('GET', f'cart/{user_id}')
    
    @classmethod
    def add_to_cart(cls, cart_data):
        """Add an item to cart"""
        return cls.make_request('POST', 'cart', data=cart_data)
    
    # Dashboard data
    @classmethod
    def get_dashboard_data(cls):
        """Get dashboard data from Flask API"""
        return cls.make_request('GET', 'dashboard') 