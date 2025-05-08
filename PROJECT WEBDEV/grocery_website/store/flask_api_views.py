from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .api_client import FlaskAPIClient
from .models import Category as DjangoCategory, Product as DjangoProduct, RegisterUser
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
import logging

logger = logging.getLogger(__name__)

# USD to INR conversion rate
USD_TO_INR_RATE = 83.5

def convert_usd_to_inr(usd_price):
    """Convert USD price to INR"""
    try:
        return round(float(usd_price) * USD_TO_INR_RATE, 2)
    except (ValueError, TypeError):
        return 0.0

def get_product_image_url(product_name):
    """Helper function to get image URL based on product name"""
    # Try most common image extensions
    for ext in ['jpg', 'png', 'jpeg', 'gif', 'jfif']:
        # Check with exact filename match
        image_url = f"http://127.0.0.1:5000/static/images/{product_name}.{ext}"
        return image_url  # Return the first matched extension
    
    # If no match, return a generic image
    return "http://127.0.0.1:5000/static/images/placeholder.jpg"

def flask_api_debug(request):
    """Debug view to check API connectivity"""
    results = {}
    
    # Try to get products
    products = FlaskAPIClient.get_products()
    results['products'] = products
    
    # Try to get categories
    categories = FlaskAPIClient.get_categories()
    results['categories'] = categories
    
    # Try to get dashboard data
    dashboard = FlaskAPIClient.get_dashboard_data()
    results['dashboard'] = dashboard
    
    # Return as pretty printed JSON
    return HttpResponse(
        f"<html><body><h1>Flask API Debug</h1><pre>{json.dumps(results, indent=4)}</pre></body></html>",
        content_type="text/html"
    )

def flask_product_list(request):
    """View that displays products from Flask API"""
    # Get products from Flask API
    flask_products = FlaskAPIClient.get_products()
    
    if 'error' in flask_products:
        messages.error(request, f"Error fetching products: {flask_products['error']}")
        flask_products = []
    
    # Process products to convert USD to INR
    for product in flask_products:
        if product.get('price'):
            product['original_price'] = product['price']  # Keep original price
            product['price'] = convert_usd_to_inr(product['price'])
        
        # Set image URL based on product name
        if product.get('name'):
            product['image_url'] = get_product_image_url(product.get('name'))
    
    # Get categories from Flask API
    flask_categories = FlaskAPIClient.get_categories()
    if 'error' in flask_categories:
        messages.error(request, f"Error fetching categories: {flask_categories['error']}")
        flask_categories = []
    
    # Filter products based on query parameters
    category_id = request.GET.get('category_id')
    search_query = request.GET.get('q')
    
    # Filter by category
    if category_id:
        flask_products = [p for p in flask_products if p.get('category_id') == int(category_id)]
    
    # Filter by search query
    if search_query:
        search_query = search_query.lower()
        flask_products = [p for p in flask_products 
                         if search_query in p['name'].lower() 
                         or (p.get('description') and search_query in p['description'].lower())]
    
    # Sort products
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        flask_products.sort(key=lambda p: float(p['price']))
    elif sort_by == 'price_high':
        flask_products.sort(key=lambda p: float(p['price']), reverse=True)
    elif sort_by == 'newest':
        # Assuming created_at is in ISO format
        flask_products.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    
    # Get Django products as well
    django_products = DjangoProduct.objects.filter(is_available=True)
    
    # Apply the same filters to Django products
    if category_id:
        django_products = django_products.filter(category_id=category_id)
    
    if search_query:
        django_products = django_products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Convert Django products to the same format as Flask products
    django_product_list = []
    for product in django_products:
        product_dict = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'image_url': request.build_absolute_uri(product.image.url) if product.image else '',
            'category_id': product.category_id if product.category else None,
            'category_name': product.category.name if product.category else 'Uncategorized',
            'source': 'django'  # Add a source indicator
        }
        django_product_list.append(product_dict)
    
    # Add source indicator to Flask products
    for product in flask_products:
        product['source'] = 'flask'
    
    # Combine Django and Flask products
    all_products = django_product_list + flask_products
    
    # Apply sorting to combined list
    if sort_by == 'price_low':
        all_products.sort(key=lambda p: float(p['price']))
    elif sort_by == 'price_high':
        all_products.sort(key=lambda p: float(p['price']), reverse=True)
    elif sort_by == 'newest':
        # For the combined list, newer items should come first
        # Django products usually come first if no specific sort
        pass
    
    # Pagination
    paginator = Paginator(all_products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Get Django categories as well
    django_categories = DjangoCategory.objects.all()
    
    # Combine categories
    all_categories = []
    django_cat_names = set()
    
    for cat in django_categories:
        django_cat_names.add(cat.name)
        product_count = DjangoProduct.objects.filter(category=cat, is_available=True).count()
        all_categories.append({
            'id': cat.id,
            'name': cat.name,
            'product_count': product_count,
            'source': 'django'
        })
    
    if 'error' not in flask_categories:
        for cat in flask_categories:
            if cat['name'] not in django_cat_names:  # Avoid duplicates
                cat_products = [p for p in flask_products if p.get('category_name') == cat['name']]
                cat['product_count'] = len(cat_products)
                cat['source'] = 'flask'
                all_categories.append(cat)
    
    context = {
        'categories': all_categories,
        'products': products_page,
        'search_query': request.GET.get('q', ''),
        'current_category': category_id,
        'sort_by': sort_by
    }
    
    return render(request, 'flask_products.html', context)

def flask_product_detail(request, product_id):
    """View that displays a single product details from Flask API"""
    # Get product from Flask API
    flask_product = FlaskAPIClient.get_product(product_id)
    
    if 'error' in flask_product:
        messages.error(request, f"Error fetching product: {flask_product['error']}")
        return redirect('flask_product_list')
    
    # Set image URL based on product name
    if flask_product.get('name'):
        flask_product['image_url'] = get_product_image_url(flask_product.get('name'))
    
    # Convert USD price to INR
    if flask_product.get('price'):
        flask_product['original_price'] = flask_product['price']  # Keep original price
        flask_product['price'] = convert_usd_to_inr(flask_product['price'])
    
    # Get related products (from same category)
    related_products = []
    if flask_product.get('category_id'):
        # Get other products from same category
        all_products = FlaskAPIClient.get_products()
        if 'error' not in all_products:
            related_products = [p for p in all_products 
                               if p.get('category_id') == flask_product['category_id'] 
                               and p['id'] != flask_product['id']][:4]  # Limit to 4 related products
            
            # Process related products (convert price and fix image URLs)
            for product in related_products:
                if product.get('price'):
                    product['original_price'] = product['price']
                    product['price'] = convert_usd_to_inr(product['price'])
                
                # Set image URL based on product name
                if product.get('name'):
                    product['image_url'] = get_product_image_url(product.get('name'))
    
    # Add Django related products based on category name
    django_related = []
    if flask_product.get('category_name'):
        # Try to find matching Django category
        try:
            django_category = DjangoCategory.objects.filter(name__icontains=flask_product['category_name']).first()
            if django_category:
                # Get products from this category
                django_products = DjangoProduct.objects.filter(
                    category=django_category, 
                    is_available=True
                )[:4]  # Limit to 4 products
                
                # Convert to format matching Flask products
                for product in django_products:
                    django_related.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'image_url': request.build_absolute_uri(product.image.url) if product.image else '',
                        'category_id': product.category_id,
                        'category_name': product.category.name,
                        'source': 'django'
                    })
        except Exception as e:
            logger.error(f"Error fetching Django related products: {str(e)}")
    
    # Add source indicator to Flask products
    for product in related_products:
        product['source'] = 'flask'
    
    # Combine related products
    all_related = related_products + django_related
    
    context = {
        'product': flask_product,
        'related_products': all_related,
        'source': 'flask'
    }
    
    return render(request, 'flask_product_detail.html', context)

def flask_category_list(request):
    """View that displays categories from Flask API"""
    # Get categories from Flask API
    flask_categories = FlaskAPIClient.get_categories()
    
    if 'error' in flask_categories:
        messages.error(request, f"Error fetching categories: {flask_categories['error']}")
        flask_categories = []
    
    context = {
        'categories': flask_categories
    }
    
    return render(request, 'flask_categories.html', context)

def flask_category_detail(request, category_id):
    """View that displays a single category with its products from Flask API"""
    # Get category from Flask API
    flask_category = FlaskAPIClient.get_category(category_id)
    
    if 'error' in flask_category:
        messages.error(request, f"Error fetching category: {flask_category['error']}")
        return redirect('flask_category_list')
    
    context = {
        'category': flask_category
    }
    
    return render(request, 'flask_category_detail.html', context)

@login_required
def sync_with_flask(request):
    """
    Synchronize Django models with Flask API
    - Sync any new products created in Django to Flask
    - Sync any new categories created in Django to Flask
    """
    if request.method == 'POST':
        # Sync categories
        django_categories = DjangoCategory.objects.all()
        flask_categories = FlaskAPIClient.get_categories()
        
        if 'error' not in flask_categories:
            # Get flask category names for comparison
            flask_category_names = {category['name'] for category in flask_categories}
            
            # Find Django categories not in Flask
            for category in django_categories:
                if category.name not in flask_category_names:
                    # Create category in Flask
                    flask_category_data = {
                        'name': category.name,
                        'description': category.description if hasattr(category, 'description') else ''
                    }
                    result = FlaskAPIClient.create_category(flask_category_data)
                    if 'error' in result:
                        messages.error(request, f"Error syncing category {category.name}: {result['error']}")
                    else:
                        messages.success(request, f"Category {category.name} synced to Flask")
        
        # Sync products
        django_products = DjangoProduct.objects.all()
        flask_products = FlaskAPIClient.get_products()
        
        if 'error' not in flask_products:
            # Get flask product names for comparison
            flask_product_names = {product['name'] for product in flask_products}
            
            # Find Django products not in Flask
            for product in django_products:
                if product.name not in flask_product_names:
                    # Get the corresponding Flask category ID
                    category_name = product.category.name if product.category else None
                    category_id = None
                    
                    if category_name:
                        # Find category ID by name
                        for cat in flask_categories:
                            if cat['name'] == category_name:
                                category_id = cat['id']
                                break
                    
                    if not category_id:
                        messages.error(request, f"Could not find Flask category for product {product.name}")
                        continue
                    
                    # Create product in Flask
                    flask_product_data = {
                        'name': product.name,
                        'description': product.description if product.description else '',
                        'price': float(product.price) if product.price else 0.0,
                        'image_url': product.image.url if product.image and hasattr(product.image, 'url') else '',
                        'stock': 100,  # Default stock value
                        'category_id': category_id
                    }
                    result = FlaskAPIClient.create_product(flask_product_data)
                    if 'error' in result:
                        messages.error(request, f"Error syncing product {product.name}: {result['error']}")
                    else:
                        messages.success(request, f"Product {product.name} synced to Flask")
        
        messages.success(request, "Synchronization with Flask API completed")
        return redirect('admin_dashboard')
    
    return render(request, 'sync_flask.html')

@login_required
def admin_dashboard(request):
    """Dashboard that displays data from Flask API"""
    # Get dashboard data from Flask API
    flask_dashboard = FlaskAPIClient.get_dashboard_data()
    
    if 'error' in flask_dashboard:
        messages.error(request, f"Error fetching dashboard data: {flask_dashboard['error']}")
        flask_dashboard = {
            'total_users': 0,
            'total_products': 0,
            'total_categories': 0,
            'top_categories': []
        }
    
    # Get Django stats for comparison
    django_stats = {
        'total_users': RegisterUser.objects.count(),
        'total_products': DjangoProduct.objects.count(),
        'total_categories': DjangoCategory.objects.count()
    }
    
    context = {
        'flask_data': flask_dashboard,
        'django_stats': django_stats
    }
    
    return render(request, 'admin_dashboard.html', context) 