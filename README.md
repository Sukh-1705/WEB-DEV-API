# Grocery E-commerce Website

A full-featured e-commerce platform built with Flask for grocery shopping, featuring user authentication, product management, shopping cart functionality, and secure payment processing.

## Features

- 🔐 User Authentication (Signup/Login)
- 🛍️ Product Catalog with Categories
- 🛒 Shopping Cart Management
- 💳 Secure Payment Processing
- 👤 User Profile Management
- 📱 Responsive Design
- 🔍 Product Search and Filtering
- ⭐ Wishlist Functionality
- 📝 User Feedback System

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **API**: RESTful API endpoints
- **Security**: Password Hashing, Session Management

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sukh-1705/WEB-DEV-API.git
cd WEB-DEV-API
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
WEB-DEV-API/
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── instance/            # Instance-specific files
└── README.md            # Project documentation
```

## API Endpoints

### User Management
- `POST /api/users` - Create new user
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get specific user

### Product Management
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get specific product
- `POST /api/products` - Create new product

### Cart Management
- `GET /api/cart/<user_id>` - Get user's cart
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/<item_id>` - Update cart item
- `DELETE /api/cart/<item_id>` - Remove item from cart

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter)
Project Link: [https://github.com/Sukh-1705/WEB-DEV-API](https://github.com/Sukh-1705/WEB-DEV-API) 