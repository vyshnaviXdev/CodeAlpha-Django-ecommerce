from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, Category
from django.db.models import Q

# -----------------------
# HOME
# -----------------------

from django.db.models import Q

# -----------------------
# HOME
# -----------------------
def home(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    products = Product.objects.all()

    # Search by product name, description, or category
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Filter by category
    if category:
        products = products.filter(category__id=category)

    categories = Category.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
    })


# -----------------------
# REGISTER
# -----------------------

def register(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        print("DATA:", username, email)

        if not username or not password:
            messages.error(request, "Fill all fields")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords not matching")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)

        messages.success(request, "Registered successfully")

        # 🔥 IMPORTANT: redirect working check
        return redirect('login')   # temporary test

    return render(request, 'register.html')

# -----------------------
# REMOVE FROM CART
# -----------------------
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if isinstance(cart, list):
        cart = {}

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


# -----------------------
# CART VIEW
# -----------------------
def cart_view(request):
    cart = request.session.get('cart', {})

    if isinstance(cart, list):
        cart = {}

    cart_items = []
    total_price = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))

            item_total = product.price * qty
            total_price += item_total

            cart_items.append({
                'product': product,
                'qty': qty,
                'item_total': item_total
            })

        except:
            continue

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# -----------------------
# CHECKOUT
# -----------------------
def checkout_view(request):
    cart = request.session.get('cart', {})

    if isinstance(cart, list):
        cart = {}

    total_price = 0

    for product_id, qty in cart.items():
        try:
            product = get_object_or_404(Product, id=int(product_id))
            total_price += product.price * qty
        except (ValueError, TypeError):
            continue

    return render(request, 'checkout.html', {
        'total_price': total_price
    })


# -----------------------
# PRODUCT DETAIL
# -----------------------
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})
# -----------------------
# ADD TO CART
# -----------------------
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    if not isinstance(cart, dict):
        cart = {}

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    print("Cart:", request.session['cart'])

    return redirect('cart')
def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


@login_required
def profile(request):
    return render(request, 'profile.html')
@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    total = 0

    for product_id, qty in cart.items():
        product = Product.objects.get(id=int(product_id))
        total += product.price * qty

    Order.objects.create(
        user=request.user,
        total_amount=total
    )

    # Clear the cart
    request.session['cart'] = {}
    request.session.modified = True

    return render(request, 'order_success.html')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'order_history.html', {
        'orders': orders
    })

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})
