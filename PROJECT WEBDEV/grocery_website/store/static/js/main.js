(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();


    // Fixed Navbar
    $(window).scroll(function () {
        if ($(window).width() < 992) {
            if ($(this).scrollTop() > 45) {
                $('.fixed-top').addClass('bg-white shadow');
            } else {
                $('.fixed-top').removeClass('bg-white shadow');
            }
        } else {
            if ($(this).scrollTop() > 45) {
                $('.fixed-top').addClass('bg-white shadow').css('top', -45);
            } else {
                $('.fixed-top').removeClass('bg-white shadow').css('top', 0);
            }
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 25,
        loop: true,
        center: true,
        dots: false,
        nav: true,
        navText : [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ],
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });

    
})(jQuery);

document.addEventListener('DOMContentLoaded', function() {
    // Initialize cart from localStorage or create empty cart
    let cart = JSON.parse(localStorage.getItem('foodyCart')) || [];
    
    // Update cart count in navbar
    updateCartCount();
    
    // Check if we're on the product page
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn, .product-item .fa-shopping-bag');
    if (addToCartButtons.length > 0) {
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (!this.closest('#cart-link')) {  // Don't prevent navigation if it's the cart link
                    // Get product details from the closest product item
                    const productItem = this.closest('.product-item');
                    const productName = productItem.querySelector('.d-block.h5').textContent;
                    const productImage = productItem.querySelector('img').src;
                    
                    // Get price (remove $ and convert to number)
                    const priceText = productItem.querySelector('.text-primary').textContent;
                    const price = parseFloat(priceText.replace('$', ''));
                    
                    // Add to cart functionality
                    addToCart(productName, price, productImage);
                }
            });
        });
    }

    // Function to add item to cart
    function addToCart(productName, price, productImage) {
        // Check if product already exists in cart
        const existingProductIndex = cart.findIndex(item => item.name === productName);
        
        if (existingProductIndex !== -1) {
            // Increment quantity if product already in cart
            cart[existingProductIndex].quantity += 1;
            cart[existingProductIndex].total = cart[existingProductIndex].quantity * cart[existingProductIndex].price;
        } else {
            // Add new product to cart
            cart.push({
                id: Date.now(), // Using timestamp as unique ID
                name: productName,
                price: price,
                image: productImage,
                quantity: 1,
                total: price
            });
        }
        
        // Save cart to localStorage
        localStorage.setItem('foodyCart', JSON.stringify(cart));
        
        // Update cart count
        updateCartCount();
        
        // Show success message
        showToast(productName + ' added to cart!');
    }
    
    // Check if we're on the cart page
    const cartItemsContainer = document.getElementById('cart-items');
    if (cartItemsContainer) {
        renderCart();
    }
    
    // Function to update cart count in navbar
    function updateCartCount() {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
            cartCountElement.textContent = totalItems;
        }
    }
    
    // Function to render cart items on cart page
    function renderCart() {
        const cartItemsContainer = document.getElementById('cart-items');
        const cartEmptyMessage = document.querySelector('.cart-empty-message');
        const cartTable = document.querySelector('.cart-table');
        const checkoutBtn = document.querySelector('.checkout-btn');
        
        // Check if cart is empty
        if (cart.length === 0) {
            cartEmptyMessage.style.display = 'block';
            cartTable.style.display = 'none';
            checkoutBtn.disabled = true;
            
            // Update totals
            document.getElementById('cart-subtotal').textContent = '$0.00';
            document.getElementById('cart-total').textContent = '$0.00';
            return;
        }
        
        // Cart has items
        cartEmptyMessage.style.display = 'none';
        cartTable.style.display = 'block';
        checkoutBtn.disabled = false;
        
        // Clear existing items
        cartItemsContainer.innerHTML = '';
        
        // Add each item to the cart
        cart.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${item.image}" alt="${item.name}" style="width: 50px; height: 50px; object-fit: cover;">
                        <span class="ms-2">${item.name}</span>
                    </div>
                </td>
                <td>$${item.price.toFixed(2)}</td>
                <td>
                    <div class="input-group" style="width: 120px;">
                        <button class="btn btn-sm btn-outline-secondary decrease-qty" data-id="${item.id}">-</button>
                        <input type="text" class="form-control text-center item-qty" value="${item.quantity}" readonly>
                        <button class="btn btn-sm btn-outline-secondary increase-qty" data-id="${item.id}">+</button>
                    </div>
                </td>
                <td>$${item.total.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-danger remove-item" data-id="${item.id}">
                        <i class="fa fa-trash"></i>
                    </button>
                </td>
            `;
            cartItemsContainer.appendChild(row);
        });
        
        // Calculate and update totals
        updateCartTotals();
        
        // Add event listeners for quantity buttons and remove buttons
        addCartEventListeners();
    }
    
    // Function to update cart totals
    function updateCartTotals() {
        const subtotal = cart.reduce((total, item) => total + item.total, 0);
        const shipping = subtotal > 0 ? 5 : 0;
        const total = subtotal + shipping;
        
        document.getElementById('cart-subtotal').textContent = '$' + subtotal.toFixed(2);
        document.getElementById('shipping-cost').textContent = '$' + shipping.toFixed(2);
        document.getElementById('cart-total').textContent = '$' + total.toFixed(2);
    }
    
    // Function to add event listeners to cart buttons
    function addCartEventListeners() {
        // Decrease quantity buttons
        document.querySelectorAll('.decrease-qty').forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                updateItemQuantity(id, -1);
            });
        });
        
        // Increase quantity buttons
        document.querySelectorAll('.increase-qty').forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                updateItemQuantity(id, 1);
            });
        });
        
        // Remove item buttons
        document.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                removeCartItem(id);
            });
        });
    }
    
    // Function to update item quantity
    function updateItemQuantity(id, change) {
        const itemIndex = cart.findIndex(item => item.id.toString() === id);
        
        if (itemIndex !== -1) {
            cart[itemIndex].quantity += change;
            
            // Remove item if quantity becomes 0 or less
            if (cart[itemIndex].quantity <= 0) {
                removeCartItem(id);
                return;
            }
            
            // Update total for this item
            cart[itemIndex].total = cart[itemIndex].quantity * cart[itemIndex].price;
            
            // Save updated cart
            localStorage.setItem('foodyCart', JSON.stringify(cart));
            
            // Re-render cart
            renderCart();
            updateCartCount();
        }
    }
    
    // Function to remove item from cart
    function removeCartItem(id) {
        cart = cart.filter(item => item.id.toString() !== id);
        
        // Save updated cart
        localStorage.setItem('foodyCart', JSON.stringify(cart));
        
        // Re-render cart
        renderCart();
        updateCartCount();
    }
    
    // Toast message function
    function showToast(message) {
        // Create toast element if it doesn't exist
        let toast = document.getElementById('toast-notification');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast-notification';
            toast.style.position = 'fixed';
            toast.style.bottom = '20px';
            toast.style.right = '20px';
            toast.style.backgroundColor = '#4CAF50';
            toast.style.color = 'white';
            toast.style.padding = '16px';
            toast.style.borderRadius = '4px';
            toast.style.zIndex = '1000';
            toast.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
            toast.style.transition = 'opacity 0.5s';
            document.body.appendChild(toast);
        }
        
        // Set message and show toast
        toast.textContent = message;
        toast.style.opacity = '1';
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
        }, 3000);
    }

    // Product Detail Page Functionality
    const productDetailContainer = document.querySelector('.product-detail');
    if (productDetailContainer) {
        // Quantity selector functionality
        const qtyInput = document.querySelector('.quantity-input');
        const qtyDecrease = document.querySelector('.quantity-decrease');
        const qtyIncrease = document.querySelector('.quantity-increase');
        
        if (qtyDecrease && qtyIncrease && qtyInput) {
            qtyDecrease.addEventListener('click', () => {
                const currentValue = parseInt(qtyInput.value);
                if (currentValue > 1) {
                    qtyInput.value = currentValue - 1;
                }
            });

            qtyIncrease.addEventListener('click', () => {
                const currentValue = parseInt(qtyInput.value);
                qtyInput.value = currentValue + 1;
            });
        }

        // Add to cart functionality for product detail page
        const addToCartBtn = document.querySelector('.add-to-cart-btn');
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const productName = document.querySelector('.product-title').textContent;
                const productImage = document.querySelector('.product-image').src;
                const priceText = document.querySelector('.product-price').textContent;
                const price = parseFloat(priceText.replace('$', ''));
                const quantity = parseInt(qtyInput.value);
                
                // Check if product already exists in cart
                const existingProductIndex = cart.findIndex(item => item.name === productName);
                
                if (existingProductIndex !== -1) {
                    // Update quantity if product already in cart
                    cart[existingProductIndex].quantity += quantity;
                    cart[existingProductIndex].total = cart[existingProductIndex].quantity * cart[existingProductIndex].price;
                } else {
                    // Add new product to cart
                    cart.push({
                        id: Date.now(),
                        name: productName,
                        price: price,
                        image: productImage,
                        quantity: quantity,
                        total: price * quantity
                    });
                }
                
                // Save cart to localStorage
                localStorage.setItem('foodyCart', JSON.stringify(cart));
                
                // Update cart count
                updateCartCount();
                
                // Show success message
                showToast(`${quantity} ${productName} added to cart!`);
            });
        }

        // Product image gallery functionality
        const thumbnails = document.querySelectorAll('.product-thumbnail');
        const mainImage = document.querySelector('.product-image');
        
        if (thumbnails.length && mainImage) {
            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    // Remove active class from all thumbnails
                    thumbnails.forEach(t => t.classList.remove('active'));
                    // Add active class to clicked thumbnail
                    this.classList.add('active');
                    // Update main image
                    mainImage.src = this.src;
                });
            });

            // Add download button functionality
            const downloadBtn = document.querySelector('.download-image-btn');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', function() {
                    // Create a temporary anchor element
                    const link = document.createElement('a');
                    link.href = mainImage.src;
                    
                    // Get the product name for the filename
                    const productName = document.querySelector('.product-title').textContent.trim();
                    const fileName = productName.toLowerCase().replace(/\s+/g, '-') + '.jpg';
                    
                    link.download = fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // Show success message
                    showToast('Image downloaded successfully!');
                });
            }
        }
    }

    // Product Search and Sort Functionality
    const productContainer = document.querySelector('.product-container');
    const searchInput = document.querySelector('#searchInput');
    const sortSelect = document.querySelector('#sortSelect');

    if (productContainer) {
        let products = Array.from(document.querySelectorAll('.product-item'));
        const originalProducts = [...products]; // Keep original order for reset

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase().trim();
                
                products.forEach(product => {
                    const productName = product.querySelector('.h5').textContent.toLowerCase();
                    const productPrice = product.querySelector('.text-primary').textContent;
                    
                    if (productName.includes(searchTerm) || productPrice.includes(searchTerm)) {
                        product.style.display = '';
                    } else {
                        product.style.display = 'none';
                    }
                });

                // Show message if no products found
                const noResults = document.querySelector('.no-results');
                const visibleProducts = products.filter(p => p.style.display !== 'none');
                
                if (visibleProducts.length === 0) {
                    if (!noResults) {
                        const message = document.createElement('div');
                        message.className = 'no-results text-center py-4';
                        message.innerHTML = '<h5>No products found matching your search.</h5>';
                        productContainer.appendChild(message);
                    }
                } else {
                    if (noResults) {
                        noResults.remove();
                    }
                }
            });
        }

        // Sort functionality
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                const sortBy = this.value;
                
                products.sort((a, b) => {
                    const priceA = parseFloat(a.querySelector('.text-primary').textContent.replace('$', ''));
                    const priceB = parseFloat(b.querySelector('.text-primary').textContent.replace('$', ''));
                    const nameA = a.querySelector('.h5').textContent.toLowerCase();
                    const nameB = b.querySelector('.h5').textContent.toLowerCase();

                    switch(sortBy) {
                        case 'price-low-high':
                            return priceA - priceB;
                        case 'price-high-low':
                            return priceB - priceA;
                        case 'name-a-z':
                            return nameA.localeCompare(nameB);
                        case 'name-z-a':
                            return nameB.localeCompare(nameA);
                        default: // Reset to original order
                            return originalProducts.indexOf(a) - originalProducts.indexOf(b);
                    }
                });

                // Clear and re-append sorted products
                productContainer.innerHTML = '';
                products.forEach(product => {
                    if (product.style.display !== 'none') {
                        productContainer.appendChild(product);
                    }
                });
            });
        }
    }

    // Function to download product images
    function downloadImage(imageUrl, productName) {
        fetch(imageUrl)
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${productName}.jpg`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Error downloading image:', error);
                showToast('Error downloading image. Please try again.', 'error');
            });
    }

    // Add click event listeners to images that should be downloadable
    const downloadableImages = document.querySelectorAll('.downloadable-image');
    downloadableImages.forEach(img => {
        img.style.cursor = 'pointer';
        img.title = 'Click to download';
        img.addEventListener('click', function() {
            const fileName = this.getAttribute('data-filename') || 'image.jpg';
            downloadImage(this.src, fileName);
        });
    });
});