# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'  # Namespace for the orders app

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),  # Add this line
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('place-order/', views.place_order, name='place_order'),
    path('payment/<str:address>/', views.payment, name='payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
]