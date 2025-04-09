from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Cart
from .models import Order, OrderItem
from django.shortcuts import redirect
from .forms import AddressForm
from django.contrib.auth.decorators import login_required
from .models import Address
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Order
from cart.models import CartItem
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Address
from .forms import AddressForm

# orders/views.py


@login_required
def checkout(request):
    if request.method == 'POST':
        # Extract shipping address from the form
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        
        # Create the shipping address string
        shipping_address = f"{street}, {city}, {state}, {zip_code}"
        
        # Redirect to the payment page with the shipping address
        return redirect('orders:payment', address=shipping_address)
    
    # If GET request, render the checkout form
    form = AddressForm()
    previous_addresses = Address.objects.filter(user=request.user).distinct()
    return render(request, 'orders/checkout.html', {'form': form, 'previous_addresses': previous_addresses})
# orders/views.py
from django.shortcuts import get_object_or_404
from .models import Order

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.all()  # Fetch all order items for this order
    return render(request, 'orders/order_detail.html', {'order': order, 'order_items': order_items})


from django.shortcuts import render, get_object_or_404
from .models import Order

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_confirmation.html', {'order': order})

from farmer.models import Notification  # Import the Notification model

@require_POST
def place_order(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to place an order.")
        return redirect('login')
    
    try:
        # Get the cart for the current user
        cart = Cart.objects.get(customer=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')
        
        # Create the order
        order = Order.objects.create(
            customer=request.user.customer,
            total_price=cart.total_price,
            shipping_address=request.POST.get('shipping_address'),
            payment_method=request.POST.get('payment_method'),
        )
        
        # Add items to the order and notify farmers
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
            
            # Create a notification for the farmer
            Notification.objects.create(
                farmer=cart_item.product.farmer,
                message=f"New order for {cart_item.product.name} (Quantity: {cart_item.quantity})",
            )
        
        # Clear the cart
        cart_items.delete()
        cart.total_price = 0
        cart.save()
        
        messages.success(request, "Order placed successfully!")
        return redirect('order_confirmation', order_id=order.id)
    
    except Cart.DoesNotExist:
        messages.error(request, "No cart found for the current user.")
        return redirect('cart')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('checkout')
    
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
import razorpay
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from django.shortcuts import render, redirect


@login_required
def payment(request, address):
    cart = get_object_or_404(Cart, customer=request.user)
    total_price = cart.total_price

    # Create the Order instance with the shipping address
    order = Order.objects.create(
        customer=request.user.customer,
        total_price=total_price,
        shipping_address=address,  # Use the shipping address entered by the customer
        payment_status='pending',
    )

    # Add items to the order
    for cart_item in cart.cartitem_set.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )

    # Create Razorpay order
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    payment_data = {
        'amount': int(total_price * 100),  # Convert to paise
        'currency': 'INR',
        'receipt': f'order_{order.id}',
        'payment_capture': 1
    }
    razorpay_order = razorpay_client.order.create(data=payment_data)

    # Save the Razorpay order ID in the Order model
    order.razorpay_order_id = razorpay_order['id']
    order.save()
    CartItem.objects.filter(cart=cart).delete()

    context = {
        'address': address,
        'total_price': total_price,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_amount': payment_data['amount'],
        'razorpay_currency': 'INR',
        'razorpay_key': settings.RAZORPAY_API_KEY,
    }

    return render(request, 'orders/payment.html', context)
# orders/views.py
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Order
import razorpay
from django.conf import settings

from cart.models import Cart, CartItem  # Import Cart and CartItem models

@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        payload = request.POST
        try:
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            razorpay_client.utility.verify_payment_signature(payload)

            # Fetch the order using razorpay_order_id
            razorpay_order_id = payload.get('razorpay_order_id')
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)

            # Update payment status
            order.payment_status = 'completed'
            order.save()

            # Notify the farmer(s) about the new order
            for item in order.order_items.all():
                Notification.objects.create(
                    farmer=item.product.farmer,
                    message=f"New order for {item.product.name} (Quantity: {item.quantity})",
                )

            # Clear the cart after successful payment
            cart = Cart.objects.get(customer=request.user)
            cart.cartitem_set.all().delete()  # Delete all cart items
            cart.total_price = 0  # Reset the total price
            cart.save()

            # Render the payment success template
            return render(request, 'orders/payment_callback.html', {
                'payment_success': True,
                'order': order,
            })
        except Order.DoesNotExist:
            return render(request, 'orders/payment_callback.html', {
                'payment_success': False,
                'error': 'Order not found.',
            })
        except Exception as e:
            return render(request, 'orders/payment_callback.html', {
                'payment_success': False,
                'error': str(e),
            })
    return render(request, 'orders/payment_callback.html', {
        'payment_success': False,
        'error': 'Invalid request.',
    })