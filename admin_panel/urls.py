from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_user_list, name='admin_user_list'),
    path('users/edit/<int:user_id>/', views.edit_user, name='admin_edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='admin_delete_user'),
    path('products/', views.admin_product_list, name='admin_product_list'),
    path('products/edit/<int:product_id>/', views.edit_product, name='admin_edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='admin_delete_product'),
    path('orders/', views.admin_order_list, name='admin_order_list'),
    path('orders/update-status/<int:order_id>/', views.update_order_status, name='admin_update_order_status'),
    path('orders/<int:order_id>/', views.order_detail, name='admin_order_detail'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),
    path('analytics/data/', views.admin_analytics_data, name='admin_analytics_data'),
]