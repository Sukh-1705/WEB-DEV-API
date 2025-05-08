from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import jsonify
from flask_cors import CORS  # Import CORS for cross-origin requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)  # Enable CORS for all routes
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))

# Add models for products and categories
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Login required decorator
def login_required(route_function):
    def decorated_route(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    decorated_route.__name__ = route_function.__name__
    return decorated_route

# API endpoints for User
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id, 
        'firstname': user.firstname,
        'lastname': user.lastname,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at
    } for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id, 
        'firstname': user.firstname,
        'lastname': user.lastname,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(
        firstname=data['firstname'],
        lastname=data['lastname'],
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'id': new_user.id,
            'message': 'User created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoints for Products
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': format_image_url(product.image_url),
        'stock': product.stock,
        'category_id': product.category_id,
        'category_name': product.category.name,
        'created_at': product.created_at
    } for product in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': format_image_url(product.image_url),
        'stock': product.stock,
        'category_id': product.category_id,
        'category_name': product.category.name,
        'created_at': product.created_at
    })

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    # Check if category exists
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        image_url=data.get('image_url', ''),
        stock=data.get('stock', 0),
        category_id=data['category_id']
    )
    
    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            'id': new_product.id,
            'message': 'Product created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoints for Categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'product_count': len(category.products)
    } for category in categories])

@app.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'products': [{
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url
        } for product in category.products]
    })

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    
    # Check if category already exists
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Category already exists'}), 400
    
    new_category = Category(
        name=data['name'],
        description=data.get('description', '')
    )
    
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({
            'id': new_category.id,
            'message': 'Category created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoint for cart items
@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_user_cart(user_id):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': item.id,
        'product_name': item.product_name,
        'quantity': item.quantity,
        'price': item.price,
        'image_url': item.image_url,
        'total_price': item.price * item.quantity
    } for item in cart_items])

@app.route('/api/cart', methods=['POST'])
def add_to_cart_api():
    data = request.get_json()
    
    # Check if item already exists in cart
    existing_item = CartItem.query.filter_by(
        user_id=data['user_id'],
        product_name=data['product_name']
    ).first()
    
    try:
        if existing_item:
            # If item exists, increment quantity
            existing_item.quantity += 1
            db.session.commit()
            item_id = existing_item.id
        else:
            # If item doesn't exist, create new cart item
            new_item = CartItem(
                user_id=data['user_id'],
                product_name=data['product_name'],
                price=float(data['price']),
                image_url=data.get('image_url', ''),
                quantity=1
            )
            db.session.add(new_item)
            db.session.commit()
            item_id = new_item.id
            
        return jsonify({
            'id': item_id,
            'message': 'Added to cart successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoint for dashboard data
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_categories = Category.query.count()
    
    # Get top categories
    categories = Category.query.all()
    top_categories = sorted(categories, key=lambda c: len(c.products), reverse=True)[:5]
    
    return jsonify({
        'total_users': total_users,
        'total_products': total_products,
        'total_categories': total_categories,
        'top_categories': [{
            'id': category.id,
            'name': category.name,
            'product_count': len(category.products)
        } for category in top_categories]
    })

# Your existing routes...
@app.route('/')
def home():
    return render_template('HomePageHTML.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')

        # Validation checks
        if not all([firstname, lastname, username, email, password, confirm_password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('signup'))

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(
            firstname=firstname,
            lastname=lastname,
            username=username,
            email=email,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('signup'))

    return render_template('Signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.firstname}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))

    return render_template('Login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

# Updated profile route
@app.route('/profile')
@login_required
def profile():
    # Get current user information
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('logout'))
    
    return render_template('Profile HTML.html', user=user)

# New route for password update
@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('logout'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate inputs
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required!', 'error')
        return redirect(url_for('profile'))
    
    # Check if current password is correct
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect!', 'error')
        return redirect(url_for('profile'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('profile'))
    
    # Update password
    try:
        user.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        flash('Password updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/get_cart')
@login_required
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    items = [{
        'id': item.id,
        'product_name': item.product_name,
        'quantity': item.quantity,
        'price': item.price,
        'image_url': item.image_url
    } for item in cart_items]
    return jsonify(items)

@app.route('/contact')
def contact():
    return render_template('Contact Form HTML.html') 

@app.route('/feedback')
def feedback():
    return render_template('Feedback Form HTML.html')  

@app.route('/about')
def about():
    return render_template('About Us HTML.html') 

@app.route('/wishlist')
@login_required
def wishlist():
    return render_template('Wishlist HTML.html') 

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    if not request.is_json:
        return jsonify({"error": "Invalid request"}), 400
        
    data = request.get_json()
    product_name = data.get('product_name')
    price = data.get('price')
    image_url = data.get('image_url')
    
    if not all([product_name, price, image_url]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            user_id=session['user_id'],
            product_name=product_name
        ).first()
        
        if existing_item:
            # If item exists, increment quantity
            existing_item.quantity += 1
            db.session.commit()
        else:
            # If item doesn't exist, create new cart item
            new_item = CartItem(
                user_id=session['user_id'],
                product_name=product_name,
                price=float(price),  # Store price as float
                image_url=image_url,
                quantity=1
            )
            db.session.add(new_item)
            db.session.commit()
            
        # Get updated cart count
        cart_count = CartItem.query.filter_by(user_id=session['user_id']).count()
        
        return jsonify({
            "message": "Added to cart successfully",
            "cart_count": cart_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Modify the shopping_cart route to calculate total correctly
@app.route('/shopping_cart')
@login_required
def shopping_cart():
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total_price = sum(item.price * item.quantity for item in cart_items)
    return render_template('Shopping Cart HTML.html', cart_items=cart_items, total_price=total_price)

@app.route('/best_deals')
def best_deals():
    return render_template('Best Deals HTML.html')

@app.route('/fruits_category')
def fruits_category():
    return render_template('Fruits Category Page HTML.html')

@app.route('/medicine_category')
def medicine_category():
    return render_template('Medicine Category Page HTML.html')

@app.route('/baby_care_category')
def baby_care_category():
    return render_template('Baby Care Category Page HTML.html')

@app.route('/office_category')
def office_category():
    return render_template('Office Category Page HTML.html')

@app.route('/beauty_category')
def beauty_category():
    return render_template('Beauty Category Page HTML.html')

@app.route('/gardening_category')
def gardening_category():
    return render_template('Gardening Category Page HTML.html')

@app.route('/feedback_confirmation')
def feedback_confirmation():
    return render_template('feedback_confirmation.html')

@app.route('/checkout')
@login_required
def checkout_page():
    return render_template('Checkout.html')

# Update the payment route to handle both GET and POST methods
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    # Get cart items for payment
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total_price = sum(item.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Get form data from payment form
        card_number = request.form.get('card_number')
        card_holder = request.form.get('card_holder')
        expiry_month = request.form.get('month')
        expiry_year = request.form.get('year')
        cvv = request.form.get('cvv')
        
        # Validate payment details (basic validation)
        if not all([card_number, card_holder, expiry_month, expiry_year, cvv]):
            flash('All payment fields are required', 'error')
            return redirect(url_for('payment'))
            
        # If payment is successful, store payment info in session
        session['payment_completed'] = True
        
        # Redirect to confirmation page
        return redirect(url_for('payment_confirmation'))
    
    # For GET request, show payment form
    delivery_info = session.get('delivery_info')
    if not delivery_info:
        return redirect(url_for('payment'))
    
    return render_template('Payment.html', 
                         delivery_info=delivery_info,
                         cart_items=cart_items,
                         total_price=total_price)

@app.route('/payment_confirmation')
def payment_confirmation():
    # Check if payment was completed
    if not session.get('payment_completed'):
        flash('Please complete payment first', 'error')
        return redirect(url_for('payment'))
    
    # Get delivery info from session
    delivery_info = session.get('delivery_info')
    if not delivery_info:
        flash('Missing delivery information', 'error')
        return redirect(url_for('checkout_page'))
    
    try:
        # Clear cart after successful payment
        CartItem.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
        
        # Clear session data
        session.pop('delivery_info', None)
        session.pop('payment_completed', None)
        
        return render_template('payment_confirmation.html')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your payment', 'error')
        return redirect(url_for('payment'))

@app.route('/update_cart_quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    if not request.is_json:
        return jsonify({"error": "Invalid request"}), 400
        
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')
    
    if not all([item_id, quantity]):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=session['user_id']
        ).first()
        
        if not cart_item:
            return jsonify({"error": "Item not found"}), 404
            
        if int(quantity) <= 0:
            # If quantity is 0 or negative, remove the item
            db.session.delete(cart_item)
        else:
            cart_item.quantity = int(quantity)
            
        db.session.commit()
        
        # Calculate new total
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        total_price = sum(item.price * item.quantity for item in cart_items)
        
        return jsonify({
            "message": "Cart updated successfully",
            "total_price": round(total_price, 2)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    if not request.is_json:
        return jsonify({"error": "Invalid request"}), 400
        
    data = request.get_json()
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({"error": "Missing item ID"}), 400
        
    try:
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=session['user_id']
        ).first()
        
        if not cart_item:
            return jsonify({"error": "Item not found"}), 404
            
        db.session.delete(cart_item)
        db.session.commit()
        
        # Calculate new total
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        total_price = sum(item.price * item.quantity for item in cart_items)
        
        return jsonify({
            "message": "Item removed successfully",
            "total_price": round(total_price, 2)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# Function to create mock data
def create_mock_data():
    # Create categories if they don't exist
    categories = [
        {"name": "Fruits", "description": "Fresh fruits from local farms"},
        {"name": "Vegetables", "description": "Fresh vegetables for your kitchen"},
        {"name": "Dairy", "description": "Milk, cheese and other dairy products"},
        {"name": "Bakery", "description": "Fresh bread and pastries"},
        {"name": "Beverages", "description": "Drinks and refreshments"}
    ]
    
    for category_data in categories:
        if not Category.query.filter_by(name=category_data["name"]).first():
            category = Category(name=category_data["name"], description=category_data["description"])
            db.session.add(category)
    
    db.session.commit()
    
    # Create products if they don't exist
    products = [
        {"name": "Apple", "description": "Fresh red apples", "price": 120.99, "image_url": "/static/images/apple.jpg", "stock": 100, "category_name": "Fruits"},
        {"name": "Banana", "description": "Yellow bananas", "price": 80.99, "image_url": "/static/images/banana.jpg", "stock": 150, "category_name": "Fruits"},
        {"name": "Orange", "description": "Juicy oranges", "price": 150.49, "image_url": "/static/images/orange.jpg", "stock": 80, "category_name": "Fruits"},
        {"name": "Tomato", "description": "Red tomatoes", "price": 100.49, "image_url": "/static/images/tomato.jpg", "stock": 100, "category_name": "Vegetables"},
        {"name": "Lettuce", "description": "Fresh green lettuce", "price": 95.89, "image_url": "/static/images/lettuce.jpg", "stock": 50, "category_name": "Vegetables"},
        {"name": "Milk", "description": "Fresh milk", "price": 75.99, "image_url": "/static/images/milk.jpg", "stock": 200, "category_name": "Dairy"},
        {"name": "Bread", "description": "Freshly baked bread", "price": 65.99, "image_url": "/static/images/bread.jpg", "stock": 30, "category_name": "Bakery"},
        {"name": "Water", "description": "Bottled water", "price": 45.49, "image_url": "/static/images/water.jpg", "stock": 300, "category_name": "Beverages"}
    ]
    
    for product_data in products:
        category = Category.query.filter_by(name=product_data["category_name"]).first()
        if category and not Product.query.filter_by(name=product_data["name"], category_id=category.id).first():
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                image_url=product_data["image_url"],
                stock=product_data["stock"],
                category_id=category.id
            )
            db.session.add(product)
    
    db.session.commit()

# Function to update prices of existing products
def update_product_prices():
    """Update prices of existing products to higher values"""
    try:
        # Price mapping dictionary
        price_updates = {
            "Apple": 120.99,
            "Banana": 80.99,
            "Orange": 150.49,
            "Tomato": 100.49,
            "Lettuce": 95.89,
            "Milk": 75.99,
            "Bread": 65.99,
            "Water": 45.49
        }
        
        # Update all existing products
        for product_name, new_price in price_updates.items():
            product = Product.query.filter_by(name=product_name).first()
            if product:
                product.price = new_price
                print(f"Updated price of {product_name} to ₹{new_price}")
        
        # Update any other products to have a minimum price of 50
        for product in Product.query.filter(Product.price < 50).all():
            if product.name not in price_updates:
                product.price = product.price * 20  # Multiply smaller prices by 20
                print(f"Updated price of {product.name} from low value to ₹{product.price}")
        
        db.session.commit()
        print("All product prices updated successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating prices: {str(e)}")

# Create database tables and load mock data
with app.app_context():
    db.create_all()
    create_mock_data()
    update_product_prices()  # Update existing product prices

def format_image_url(image_url):
    """Format image URL to ensure it's properly formed.
    This function normalizes image URLs to use the correct path format."""
    if not image_url:
        return ''
    
    # If it's already a full URL, return as is
    if image_url.startswith('http'):
        return image_url
    
    # If it just has a filename, add the static/images path
    if not '/' in image_url:
        return f"/static/images/{image_url}"
    
    # If it has a path without /static, add it
    if not image_url.startswith('/static') and not image_url.startswith('static'):
        if image_url.startswith('/'):
            return f"/static{image_url}"
        else:
            return f"/static/{image_url}"
    
    # If it starts with static/ without a /, add it
    if image_url.startswith('static/'):
        return f"/{image_url}"
    
    return image_url

if __name__ == '__main__':
    app.run(debug=True)