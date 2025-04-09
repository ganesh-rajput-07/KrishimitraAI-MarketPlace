# farmer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Farmer, Product, Notification
from .forms import ProductForm, FarmerProfileForm
from orders.models import Order

# farmer/views.py
@login_required
def farmer_dashboard(request):
    farmer = request.user.farmer
    products = Product.objects.filter(farmer=farmer)
    
    # Fetch orders that include products from this farmer
    order_items = OrderItem.objects.filter(product__farmer=farmer).select_related('order')
    orders = {item.order for item in order_items}  # Use a set to avoid duplicate orders
    
    notifications = Notification.objects.filter(farmer=farmer, is_read=False)
    total_earnings = sum(order.total_price for order in orders)

    context = {
        'farmer': farmer,
        'products': products,
        'orders': orders,
        'notifications': notifications,
        'total_earnings': total_earnings,
    }
    
    return render(request, 'farmer/dashboard.html', context)
@login_required
def farmer_product_list(request):
    farmer = request.user.farmer
    products = Product.objects.filter(farmer=farmer)
    return render(request, 'farmer/product_list.html', {'products': products})

# farmer/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user.farmer  # Associate the product with the logged-in farmer
            product.save()  # Save the product to the database
            return redirect('farmer_product_list')  # Redirect to the product list page
    else:
        form = ProductForm()
    return render(request, 'farmer/add_product.html', {'form': form})
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user.farmer)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('farmer_product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'farmer/edit_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, farmer=request.user.farmer)
    product.delete()
    return redirect('farmer_product_list')


# farmer/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem

# farmer/views.py
@login_required
def farmer_orders(request):
    farmer = request.user.farmer
    
    # Fetch order items where the product belongs to the logged-in farmer
    order_items = OrderItem.objects.filter(product__farmer=farmer).select_related('order')
    
    # Extract unique orders from the order items
    orders = {item.order for item in order_items}
    
    return render(request, 'farmer/orders.html', {'orders': orders})
@login_required
def update_order_status(request, order_id):
    
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        return redirect('farmer_orders')
    return render(request, 'farmer/update_order_status.html', {'order': order})

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FarmerProfileForm, UserForm
from .models import Farmer
@login_required
def farmer_profile(request):
    farmer = request.user.farmer  # Fetch the farmer profile
    return render(request, 'farmer/profile.html', {'farmer': farmer})
@login_required
def farmer_notifications(request):
    farmer = request.user.farmer
    notifications = Notification.objects.filter(farmer=farmer)
    return render(request, 'farmer/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, farmer=request.user.farmer)
    notification.is_read = True
    notification.save()
    return redirect('farmer_notifications')

# farmer/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FarmerProfileForm, UserForm
from .models import Farmer

@login_required
def edit_profile_farmer(request):
    farmer = request.user.farmer
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('farmer_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = FarmerProfileForm(instance=farmer)
    
    return render(request, 'farmer/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# farmer/views.py
# farmer/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderItem
from django.db.models import Count, Sum
from datetime import timedelta
from django.utils import timezone

@login_required
def farmer_analytics(request):
    farmer = request.user.farmer
    
    # Fetch orders for the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Group orders by day and calculate total orders and earnings per day
    orders = OrderItem.objects.filter(
        product__farmer=farmer,
        order__created_at__range=(start_date, end_date)
    ).values('order__created_at__date').annotate(
        total_orders=Count('id'),
        total_earnings=Sum('product__base_price')  # Use 'base_price' instead of 'price'
    ).order_by('order__created_at__date')
    
    # Prepare data for the chart
    dates = [order['order__created_at__date'].strftime('%Y-%m-%d') for order in orders]
    total_orders = [order['total_orders'] for order in orders]
    total_earnings = [float(order['total_earnings']) for order in orders]
    
    context = {
        'farmer': farmer,
        'dates': dates,
        'total_orders': total_orders,
        'total_earnings': total_earnings,
    }
    
    return render(request, 'farmer/analytics.html', context)