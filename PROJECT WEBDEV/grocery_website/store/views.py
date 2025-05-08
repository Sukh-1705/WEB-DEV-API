from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Product, Cart, CartItem, Category, ProductReview, RegisterUser, Order, OrderItem, Address
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.db.models import Q, Avg
from django.utils.text import slugify
import os
import uuid
from .forms import CustomUserCreationForm, EmailAuthenticationForm, UserProfileForm, AddressForm
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import FileResponse
import mimetypes
from .api_client import FlaskAPIClient
import logging

logger = logging.getLogger(__name__)

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If there is a session cart, merge it
        session_cart_id = request.session.get('cart_id')
        if session_cart_id:
            try:
                session_cart = Cart.objects.get(session_id=session_cart_id, user__isnull=True)
                # Move items from session cart to user cart
                for item in session_cart.items.all():
                    user_cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                    if not created:
                        user_cart_item.quantity += item.quantity
                        user_cart_item.save()
                    else:
                        user_cart_item.quantity = item.quantity
                        user_cart_item.save()
                session_cart.delete()
                del request.session['cart_id']
            except Cart.DoesNotExist:
                pass
        return cart
    else:
        if 'cart_id' not in request.session:
            request.session['cart_id'] = str(uuid.uuid4())
        cart, created = Cart.objects.get_or_create(session_id=request.session['cart_id'], user__isnull=True)
        return cart

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Get the full path to the image
    image_path = None
    if settings.STATIC_ROOT:
        image_path = os.path.join(settings.STATIC_ROOT, 'img', 'products', f"{slugify(product.name)}.jpg")
        image_exists = os.path.exists(image_path)
    else:
        image_exists = False
    
    context = {
        'product': product,
        'related_products': related_products,
        'debug': settings.DEBUG,
        'image_path': image_path,
        'image_exists': image_exists,
    }
    
    return render(request, 'product_detail.html', context)

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

def product(request):
    # Get all categories for the filter sidebar
    categories = Category.objects.all()
    
    # Get the base queryset with default ordering
    products = Product.objects.filter(is_available=True).order_by('-created')
    
    # Handle category filter
    category_type = request.GET.get('category')
    if category_type:
        products = products.filter(category__type=category_type)
    
    # Handle search query
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Handle sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'current_category': category_type,
        'sort_by': sort_by
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # For AJAX requests, return only the product list
        html = render_to_string(
            'partials/product_list.html',
            context,
            request=request
        )
        return JsonResponse({
            'html': html,
            'has_next': products.has_next()
        })
    
    return render(request, 'product.html', context)

def testimonial(request):
    return render(request, 'testimonial.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def feature(request):
    return render(request, 'feature.html')

def blog(request):
    return render(request, 'blog.html')

def error_404(request):
    return render(request, 'error_404.html')

def feature_contact(request):
    return render(request, 'contact.html')

def feature_testimonial(request):
    return render(request, 'testimonial.html')

def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.filter(saved_for_later=False)
    saved_items = cart.items.filter(saved_for_later=True)
    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'saved_items': saved_items
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    messages.success(request, f"{product.name} added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'product'))

def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart_view')

def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.name} removed from cart!")
    return redirect('cart_view')

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('product')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'checkout.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('cart_view')
        
        try:
            # Split full name into first and last name
            full_name = request.POST.get('full_name', '').strip()
            first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
            # Create order
            order = Order.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=request.user.email,
                phone=request.POST.get('phone'),
                address_line1=request.POST.get('address_line1'),
                address_line2=request.POST.get('address_line2', ''),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zip_code=request.POST.get('postal_code'),
                payment_method=request.POST.get('payment_method'),
                total_amount=cart.get_total_price()
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.get_discounted_price()
                )
            
            # Clear the cart
            cart.delete()
            if 'cart_id' in request.session:
                del request.session['cart_id']
            
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_success', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'Error placing order: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})

def save_for_later(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.saved_for_later = not cart_item.saved_for_later
    cart_item.save()
    
    action = "saved for later" if cart_item.saved_for_later else "moved to cart"
    messages.success(request, f"{cart_item.product.name} {action}!")
    return redirect('cart_view')

def update_cart_note(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.notes = request.POST.get('note')
        cart_item.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def admin_products(request):
    return render(request, 'admin/products.html')

def admin_product_create(request):
    # TODO: Implement product creation
    # When a product is created, also sync to Flask API
    if request.method == 'POST':
        # Process form data and create product
        # ...
        
        # Sync with Flask API
        try:
            # Get category in Flask API
            flask_categories = FlaskAPIClient.get_categories()
            category_id = None
            
            if 'error' not in flask_categories:
                # Find matching category by name
                for cat in flask_categories:
                    if cat['name'] == product.category.name:
                        category_id = cat['id']
                        break
            
            if category_id:
                # Create product in Flask API
                flask_product_data = {
                    'name': product.name,
                    'description': product.description or '',
                    'price': float(product.price),
                    'image_url': product.image.url if product.image else '',
                    'stock': 100,  # Default stock
                    'category_id': category_id
                }
                
                flask_response = FlaskAPIClient.create_product(flask_product_data)
                
                if 'error' in flask_response:
                    logger.error(f"Error creating product in Flask API: {flask_response['error']}")
                else:
                    logger.info(f"Product {product.name} created in Flask API successfully")
            else:
                logger.warning(f"Could not find matching Flask category for {product.category.name}")
        except Exception as e:
            logger.error(f"Exception while creating product in Flask API: {str(e)}")
    
    return render(request, 'admin_product_create.html')

def admin_product_edit(request, pk):
    return render(request, 'admin/product_form.html')

def admin_product_delete(request, pk):
    return redirect('admin_products')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Register user in Flask API too
            try:
                flask_user_data = {
                    'firstname': user.first_name,
                    'lastname': user.last_name,
                    'username': user.email.split('@')[0],  # Use email prefix as username
                    'email': user.email,
                    'password': form.cleaned_data['password1']  # Use the plaintext password before hashing
                }
                
                # Call Flask API to create user
                flask_response = FlaskAPIClient.create_user(flask_user_data)
                
                if 'error' in flask_response:
                    logger.error(f"Error creating user in Flask API: {flask_response['error']}")
                else:
                    logger.info(f"User {user.email} registered in Flask API successfully")
            except Exception as e:
                logger.error(f"Exception while registering user in Flask API: {str(e)}")
            
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # EmailAuthenticationForm uses username field for email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@require_POST
def add_to_cart_ajax(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Product ID is required'
            }, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Product not found'
            }, status=404)
        
        # Get or create cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if 'cart_id' not in request.session:
                request.session['cart_id'] = str(uuid.uuid4())
            cart, created = Cart.objects.get_or_create(session_id=request.session['cart_id'])
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Get updated cart count
        cart_count = cart.get_total_items()
        
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} added to cart',
            'cart_count': cart_count
        })
        
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def profile(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        elif 'add_address' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
                messages.success(request, 'Address added successfully!')
                return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        address_form = AddressForm()
    
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'form': form,
        'address_form': address_form,
        'addresses': addresses
    })

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('profile')

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated successfully!')
    return redirect('profile')

def get_product_image(request, product_id):
    """
    View to serve product images
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        if product.image:
            # Get the file path
            file_path = product.image.path
            
            # Check if file exists
            if os.path.exists(file_path):
                # Get the file's mime type
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type is None:
                    content_type = 'application/octet-stream'
                
                # Open and serve the file
                response = FileResponse(open(file_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                return response
            
        # If no image or file doesn't exist, return a default image
        default_image_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'img', 'no-image.png')
        if os.path.exists(default_image_path):
            return FileResponse(open(default_image_path, 'rb'), content_type='image/png')
        
        # If no default image, return 404
        return HttpResponse(status=404)
        
    except Exception as e:
        return HttpResponse(status=404)



