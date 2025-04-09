from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/farmer/', views.farmer_register, name='farmer_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('role-selection/', views.role_selection, name='role_selection'),  # Add this line
]