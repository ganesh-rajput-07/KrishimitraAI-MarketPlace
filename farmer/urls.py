# farmer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.farmer_dashboard, name='farmer_dashboard'),
    path('products/', views.farmer_product_list, name='farmer_product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.farmer_orders, name='farmer_orders'),
    path('orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('analytics/', views.farmer_analytics, name='farmer_analytics'),
   
    path('notifications/', views.farmer_notifications, name='farmer_notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('profile/', views.farmer_profile, name='farmer_profile'),
    path('profile/edit/', views.edit_profile_farmer, name='edit_profile_farmer'),
]