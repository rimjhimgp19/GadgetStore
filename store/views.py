


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Product, CartItem, Order
from .models import Product  # adjust model import if needed
from .models import Order, OrderItem, CartItem, Product
from .models import CartItem, Order, OrderItem, OrderHistory
from django.utils import timezone



def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_page = request.GET.get('next', 'dashboard')  # Default to 'dashboard' if no 'next' is provided
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'store/login.html')


# Home page showing all products (requires login)
@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

# Register new user
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after registration
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CartItem
from django.shortcuts import get_object_or_404

@login_required
def cart_view(request):
    # Fetch cart items for the logged-in user
    cart_items = CartItem.objects.filter(user=request.user)

    # Initialize the total amount
    total = 0

    # Loop through cart items and calculate subtotal
    for cart_item in cart_items:
        subtotal = cart_item.product.price * cart_item.quantity
        total += subtotal
        cart_item.subtotal = subtotal  # Update the subtotal field

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })







# View order history for logged-in user
@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/orders.html', {'orders': orders})

# Dashboard view for logged-in user
@login_required
def dashboard(request):
    # You can pass in whatever context you like, e.g. recent orders or personalized data
    return render(request, 'store/dashboard.html')




from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Product, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} items in stock!")
        return redirect('products')

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f"Cannot add more than {product.stock}.")
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in cart.")
    else:
        messages.success(request, f"{product.name} added to cart.")

    return redirect('cart')











# def products(request):
#     all_products = Product.objects.all()
#     return render(request, 'store/products.html', {'products': all_products})



from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import CartItem, Product

# View to increase/decrease quantity in the cart
def update_cart(request, product_id):
    action = request.POST.get('action')
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(user=request.user, product=product)

    if action == 'increase':
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.name} quantity increased.")
        else:
            messages.error(request, f"Only {product.stock} items left in stock.")
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f"{product.name} quantity decreased.")
    return redirect('cart')

# View to remove item from the cart
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.name} removed from cart.")
    return redirect('cart')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem, Order
from decimal import Decimal




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, OrderItem, CartItem
from django.contrib.auth.decorators import login_required

@login_required




def place_order(request):
    # Get the user's cart items
    cart_items = CartItem.objects.filter(user=request.user)

    # Check if the cart is empty
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')  # Redirect to the cart page if the cart is empty

    # Create an Order instance
    order = Order.objects.create(
        user=request.user,
        total=0  # This will be calculated after adding OrderItems
    )

    total_amount = 0
    order_id = f"ORD-{order.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    # Create OrderItems from CartItems and calculate total
    for cart_item in cart_items:
        product = cart_item.product
        quantity = cart_item.quantity
        subtotal = cart_item.subtotal

        # Check if there's sufficient stock for the product
        if product.stock < quantity:
            messages.error(request, f"Insufficient stock for {product.name}. Available stock: {product.stock}")
            return redirect('cart')  # Redirect back to the cart if stock is insufficient

        # Create an OrderItem for each CartItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=subtotal
        )

        # Save the OrderHistory
        OrderHistory.objects.create(
            user=request.user,
            order_id=order_id,
            product_name=product.name,
            quantity=quantity,
            total_price=subtotal
        )

        # Update the total amount for the order
        total_amount += subtotal

        # Reduce the stock by the quantity ordered
        product.stock -= quantity
        product.save()

    # Update the total amount for the order
    order.total = total_amount
    order.save()

    # Clear the user's cart by deleting all CartItems
    cart_items.delete()

    # Redirect to the order confirmation page
    return redirect('order_confirmation', order_id=order.id)












from django.shortcuts import render
from django.contrib.auth.models import User
from store.models import OrderHistory

def order_history(request):
    
    order_history = OrderHistory.objects.filter(user=request.user)
  
    
    return render(request, 'store/order_history.html', {'order_history': order_history})




@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})







from django.shortcuts import render, get_object_or_404
from .models import Order

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_confirmation.html', {'order': order})


from django.shortcuts import render
from .models import Product, CartItem
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def dashboard(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    cart_products = [item.product for item in cart_items]

    all_products = list(Product.objects.all())
    product_descriptions = [f"{p.name} {p.category.name} {p.description}" for p in all_products]

    if cart_products:
      
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(product_descriptions)

        cart_indices = [all_products.index(p) for p in cart_products]

       
        cart_vector = np.mean(tfidf_matrix[cart_indices].toarray(), axis=0).reshape(1, -1)

        similarities = cosine_similarity(cart_vector, tfidf_matrix).flatten()

        recommended_indices = similarities.argsort()[::-1]
        recommended_products = [
            all_products[i] for i in recommended_indices if all_products[i] not in cart_products
        ][:5]
    else:
        recommended_products = []

    context = {
        'cart_items': cart_items,
        'recommended_products': recommended_products,
    }

    return render(request, 'store/dashboard.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})





from django.shortcuts import render
from .models import Product, Category

def products(request):
    # Get filter parameters from the GET request
    category_id = request.GET.get('category')
    price_min = request.GET.get('price_min', 0)
    price_max = request.GET.get('price_max', 9999999)

    # Fetch categories for filter dropdown
    categories = Category.objects.all()

    # Start with all products
    products = Product.objects.all()

    # Apply category filter if selected
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Apply price range filter if provided
    if price_min and price_max:
        products = products.filter(price__gte=price_min, price__lte=price_max)

    # Render the page with filtered products and category options
    return render(request, 'store/products.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'price_min': price_min,
        'price_max': price_max,
    })

