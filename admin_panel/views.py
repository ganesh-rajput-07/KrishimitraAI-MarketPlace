from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from farmer.models import Product
from orders.models import Order

@login_required
def admin_dashboard(request):
    # Fetch key metrics
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_earnings = sum(order.total_price for order in Order.objects.all())

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_earnings': total_earnings,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'admin_panel/user_list.html', {'users': users})

@login_required
def admin_product_list(request):
    products = Product.objects.all()
    return render(request, 'admin_panel/product_list.html', {'products': products})

@login_required
def admin_order_list(request):
    orders = Order.objects.all()
    return render(request, 'admin_panel/order_list.html', {'orders': orders})

from farmer.models import Notification

@login_required
def admin_notifications(request):
    notifications = Notification.objects.filter(is_read=False)
    return render(request, 'admin_panel/notifications.html', {'notifications': notifications})

from django.shortcuts import render, get_object_or_404, redirect
from farmer.models import Product
from django.contrib import messages

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        # Handle form submission to update the product
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.category = request.POST.get('category')
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_product_list')
    return render(request, 'admin_panel/edit_product.html', {'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('admin_product_list')

from orders.models import Order

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, 'Order status updated successfully!')
        return redirect('admin_order_list')
    return render(request, 'admin_panel/admin_update_order_status.html', {'order': order})

from django.contrib.auth.models import User

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Handle form submission to update the user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('admin_user_list')
    return render(request, 'admin_panel/edit_user.html', {'user': user})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('admin_user_list')

from django.shortcuts import render, get_object_or_404
from orders.models import Order

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_panel/order_detail.html', {'order': order})

# admin/views.py
# admin_panel/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Sum
from orders.models import Order
from django.contrib.auth.models import User

@login_required
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access this view
def admin_analytics(request):
    # Fetch data for the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Users Data
    users = User.objects.filter(date_joined__range=(start_date, end_date))
    users_by_date = users.extra({'date_joined': "date(date_joined)"}).values('date_joined').annotate(count=Count('id')).order_by('date_joined')
    
    # Orders Data
    orders = Order.objects.filter(created_at__range=(start_date, end_date))
    orders_by_date = orders.extra({'created_at': "date(created_at)"}).values('created_at').annotate(count=Count('id'), total_earnings=Sum('total_price')).order_by('created_at')
    
    # Prepare data for the charts
    dates = [(start_date + timedelta(days=i)).date() for i in range(30)]  # List of datetime.date objects
    
    users_data = [0] * 30
    for entry in users_by_date:
        entry_date = datetime.strptime(entry['date_joined'], '%Y-%m-%d').date()  # Convert string to datetime.date
        index = (entry_date - start_date.date()).days
        if 0 <= index < 30:  # Ensure the index is within the range
            users_data[index] = entry['count']
    
    orders_data = [0] * 30
    earnings_data = [0] * 30
    for entry in orders_by_date:
        entry_date = datetime.strptime(entry['created_at'], '%Y-%m-%d').date()  # Convert string to datetime.date
        index = (entry_date - start_date.date()).days
        if 0 <= index < 30:  # Ensure the index is within the range
            orders_data[index] = entry['count']
            earnings_data[index] = float(entry['total_earnings'])
    
    context = {
        'dates': [date.strftime('%Y-%m-%d') for date in dates],  # Convert dates to strings for the template
        'users_data': users_data,
        'orders_data': orders_data,
        'earnings_data': earnings_data,
    }
    
    return render(request, 'admin_panel/analytics.html', context)

# admin_panel/views.py
from django.http import JsonResponse

def admin_analytics_data(request):
    # Fetch data for the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Users Data
    users = User.objects.filter(date_joined__range=(start_date, end_date))
    users_by_date = users.extra({'date_joined': "date(date_joined)"}).values('date_joined').annotate(count=Count('id')).order_by('date_joined')
    
    # Orders Data
    orders = Order.objects.filter(created_at__range=(start_date, end_date))
    orders_by_date = orders.extra({'created_at': "date(created_at)"}).values('created_at').annotate(count=Count('id'), total_earnings=Sum('total_price')).order_by('created_at')
    
    # Prepare data for the charts
    dates = [(start_date + timedelta(days=i)).date() for i in range(30)]
    
    users_data = [0] * 30
    for entry in users_by_date:
        entry_date = datetime.strptime(entry['date_joined'], '%Y-%m-%d').date()
        index = (entry_date - start_date.date()).days
        if 0 <= index < 30:
            users_data[index] = entry['count']
    
    orders_data = [0] * 30
    earnings_data = [0] * 30
    for entry in orders_by_date:
        entry_date = datetime.strptime(entry['created_at'], '%Y-%m-%d').date()
        index = (entry_date - start_date.date()).days
        if 0 <= index < 30:
            orders_data[index] = entry['count']
            earnings_data[index] = float(entry['total_earnings'])
    
    data = {
        'dates': [date.strftime('%Y-%m-%d') for date in dates],
        'users_data': users_data,
        'orders_data': orders_data,
        'earnings_data': earnings_data,
    }
    
    return JsonResponse(data)