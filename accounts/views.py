# accounts/views.py
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from customer.models import Customer
from django.contrib.auth import logout
from farmer.models import Farmer
from admin_panel.models import Admin 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages



def customer_register(request):
    if request.method == 'POST':
        # Extract data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        # Validate passwords match
        if password1 != password2:
            return render(request, 'accounts/customer_register.html', {'error': 'Passwords do not match'})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/customer_register.html', {'error': 'Username already exists'})

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Create the customer profile
            Customer.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
            )

            # Log the user in
            login(request, user)
            return redirect('customer_home')
        except Exception as e:
            return render(request, 'accounts/customer_register.html', {'error': str(e)})
    return render(request, 'accounts/customer_register.html')
# accounts/views.py


def farmer_register(request):
    if request.method == 'POST':
        # Extract data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        farm_name = request.POST.get('farm_name')
        location = request.POST.get('location')
        phone_number = request.POST.get('phone_number')

        # Validate passwords match
        if password1 != password2:
            return render(request, 'accounts/farmer_register.html', {'error': 'Passwords do not match'})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/farmer_register.html', {'error': 'Username already exists'})

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Create the farmer profile
            Farmer.objects.create(
                user=user,
                farm_name=farm_name,
                location=location,
                phone_number=phone_number,
            )

            # Log the user in
            login(request, user)
            return redirect('farmer_dashboard')
        except Exception as e:
            return render(request, 'accounts/farmer_register.html', {'error': str(e)})
    return render(request, 'accounts/farmer_register.html')

# accounts/views.py

def admin_register(request):
    if request.method == 'POST':
        # Extract data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')

        # Validate passwords match
        if password1 != password2:
            return render(request, 'accounts/admin_register.html', {'error': 'Passwords do not match'})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/admin_register.html', {'error': 'Username already exists'})

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.is_staff = True  # Make the user a staff member (admin)
            user.is_superuser = True  # Make the user a superuser (admin)
            user.save()

            # Create the admin profile
            Admin.objects.create(
                user=user,
                phone_number=phone_number,
            )

            # Log the user in
            login(request, user)
            return redirect('admin_dashboard')
        except Exception as e:
            return render(request, 'accounts/admin_register.html', {'error': str(e)})
    return render(request, 'accounts/admin_register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif hasattr(user, 'farmer'):
                    return redirect('farmer_dashboard')
                else:
                    return redirect('customer_home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def role_selection(request):
    roles = [
        {'name': 'Customer', 'url': 'customer_register', 'description': 'Register as a customer to buy products.'},
        {'name': 'Farmer', 'url': 'farmer_register', 'description': 'Register as a farmer to sell products.'},
        {'name': 'Admin', 'url': 'admin_register', 'description': 'Register as an admin to manage the platform.'},
    ]
    return render(request, 'accounts/role_selection.html', {'roles': roles})