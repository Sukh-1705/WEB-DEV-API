from django.urls import path
from . import views
from . import flask_api_views
from . import flask_api_consumer

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('product/', views.product, name='product'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('feature/', views.feature, name='feature'),
    path('feature/contact.html', views.feature_contact, name='feature_contact'),
    path('feature/testimonial.html', views.feature_testimonial, name='feature_testimonial'),
    path('blog/', views.blog, name='blog'),
    path('error-404/', views.error_404, name='error_404'),
    
    # Authentication URLs
    path('signup/', views.signup_view, name='signuppage'),
    path('login/', views.login_view, name='loginpage'),
    path('logout/', views.logout_view, name='logoutpage'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/save-for-later/<int:item_id>/', views.save_for_later, name='save_for_later'),
    path('cart/note/<int:item_id>/', views.update_cart_note, name='update_cart_note'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    
    # Admin Product Management URLs
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/edit/<int:pk>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/delete/<int:pk>/', views.admin_product_delete, name='admin_product_delete'),
    path('add-to-cart-ajax/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('order-history/', views.order_history, name='order_history'),
    path('profile/', views.profile, name='profile'),
    path('profile/address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('profile/address/set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    
    # Product image URL
    path('product/image/<int:product_id>/', views.get_product_image, name='product_image'),
    
    # Flask API Integration URLs
    path('flask-api/products/', flask_api_views.flask_product_list, name='flask_product_list'),
    path('flask-api/products/<int:product_id>/', flask_api_views.flask_product_detail, name='flask_product_detail'),
    path('flask-api/categories/', flask_api_views.flask_category_list, name='flask_category_list'),
    path('flask-api/categories/<int:category_id>/', flask_api_views.flask_category_detail, name='flask_category_detail'),
    path('flask-api/sync/', flask_api_views.sync_with_flask, name='sync_with_flask'),
    path('flask-api/dashboard/', flask_api_views.admin_dashboard, name='admin_dashboard'),
    path('flask-api/add-to-cart/', flask_api_consumer.add_flask_product_to_cart, name='add_flask_product_to_cart'),
    path('flask-api/debug/', flask_api_views.flask_api_debug, name='flask_api_debug'),
]