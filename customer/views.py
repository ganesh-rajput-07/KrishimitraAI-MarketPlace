# customer/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from farmer.models import Product
from .models import Customer, Wishlist, Review
from .forms import ProfileForm, ReviewForm, UserForm
from django.contrib import messages

from django.db.models import Q  # Import for search functionality

from django.db.models import Avg

@login_required
def customer_home(request):
    query = request.GET.get('q', '')  # Get search query from request
    category = request.GET.get('category', '')  # Get category filter from request

    products = Product.objects.annotate(
        average_rating=Avg('reviews__rating')
    ).all()

    # Apply search filter
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Apply category filter
    if category:
        products = products.filter(category=category)

    return render(request, 'customer/home.html', {
        'products': products,
        'query': query,
        'category': category
    })

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'customer/product_detail.html', {'product': product})

@login_required
def wishlist(request):
    wishlist = get_object_or_404(Wishlist, customer=request.user.customer)
    return render(request, 'customer/wishlist.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(customer=request.user.customer)
    wishlist.products.add(product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, customer=request.user.customer)
    wishlist.products.remove(product)
    return redirect('wishlist')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Customer

@login_required
def profile(request):
    customer = request.user.customer  # Fetch the customer profile
    return render(request, 'customer/profile.html', {'customer': customer})
# customer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Customer, Review
from .forms import ReviewForm

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user.customer  # Assign the Customer instance, not the User instance
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'customer/submit_review.html', {'form': form, 'product': product})
# customer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Customer
from .forms import ProfileForm

@login_required
def edit_profile(request):
    customer = request.user.customer
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=customer)
    return render(request, 'customer/edit_profile.html', {'form': form})

# customer/views.py
from django.shortcuts import render
from orders.models import Order

def order_history(request):
    # Fetch orders for the logged-in customer
    orders = Order.objects.filter(customer=request.user.customer)
    return render(request, 'customer/order_history.html', {'orders': orders})