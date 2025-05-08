from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from .models import (
    attacarousel, Category, Product, Cart, CartItem,
    ProductReview, RegisterUser, Order, OrderItem, Address
)

@admin.register(attacarousel)
class AttaCarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created')
    list_filter = ('type',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount', 'is_available', 'created')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'discount', 'is_available')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at', 'updated_at')
    search_fields = ('user__email', 'session_id')
    list_filter = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'saved_for_later', 'added_at')
    list_filter = ('saved_for_later', 'added_at')
    search_fields = ('product__name', 'cart__user__email')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'email', 'comment', 'product__name')

@admin.register(RegisterUser)
class RegisterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'avatar_url')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_total')
    fields = ('product', 'quantity', 'price', 'get_total')
    
    def get_total(self, obj):
        return obj.price * obj.quantity
    get_total.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'payment_status', 'payment_status_colored', 'payment_method', 'items_count', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    list_editable = ('payment_status',)
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'order_notes')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = 'Customer'
    
    def payment_status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.payment_status, 'black'),
            obj.get_payment_status_display()
        )
    payment_status_colored.short_description = 'Status'
    
    def items_count(self, obj):
        count = obj.items.count()
        url = reverse('admin:store_orderitem_changelist') + f'?order__id={obj.id}'
        return format_html('<a href="{}">{} items</a>', url, count)
    items_count.short_description = 'Items'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sales-dashboard/', self.admin_site.admin_view(self.sales_dashboard_view), name='sales_dashboard'),
        ]
        return custom_urls + urls
    
    def sales_dashboard_view(self, request):
        # Get sales summary data
        total_sales = Order.objects.filter(payment_status='completed').aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        # Calculate average order value
        avg_order_value = 0
        if total_sales['count'] and total_sales['count'] > 0:
            avg_order_value = total_sales['total'] / total_sales['count']
        
        # Get pending orders count
        pending_orders = Order.objects.filter(payment_status='pending').count()
        
        # Get recent orders
        recent_orders = Order.objects.all().order_by('-created_at')[:10]
        
        # Get top products
        top_products = Product.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5]
        
        # Sales by month
        from django.db.models.functions import TruncMonth
        sales_by_month = Order.objects.filter(
            payment_status='completed'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('month')
        
        context = {
            'title': 'Sales Dashboard',
            'total_sales': total_sales,
            'recent_orders': recent_orders,
            'top_products': top_products,
            'sales_by_month': sales_by_month,
            'pending_orders': pending_orders,
            'avg_order_value': avg_order_value,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(request, 'admin/sales_dashboard.html', context)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total', 'created_at')
    list_filter = ('created_at', 'order__payment_status')
    search_fields = ('order__user__email', 'product__name')
    
    def get_total(self, obj):
        return obj.price * obj.quantity
    get_total.short_description = 'Total'

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line1', 'city', 'state', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('user__email', 'address_line1', 'city', 'state')
