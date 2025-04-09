# cart/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from farmer.models import Product
from .models import Cart, CartItem

# cart/views.py
# cart/views.py
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
    cart_item.save()

    # Update cart total based on the product's price
    cart.total_price += product.price
    cart.save()

    return redirect('cart:cart')
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CartItem

@login_required
def remove_from_cart(request, cart_item_id):
    # Fetch the cart item to be removed
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user)
    
    # Delete the cart item
    cart_item.delete()
    
    # Redirect back to the cart page
    return redirect('cart:cart')
@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = cart.cartitem_set.all()
    
    if request.method == 'POST':
        # Handle quantity updates
        for item in cart_items:
            new_quantity = request.POST.get(f'quantity_{item.id}')
            if new_quantity and new_quantity.isdigit():
                item.quantity = int(new_quantity)
                item.save()
        
        # Recalculate the total price of the cart
        cart.total_price = sum(item.product.price * item.quantity for item in cart_items)
        cart.save()
        
        return redirect('cart:cart')
    
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'cart_items': cart_items})