# farmer/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer')
    farm_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    VARIATION_CHOICES = [
        ('kg','Kilogram'),
        ('L','Litre'),
        ('Dozen','Dozen'),
        ('Piece','Piece'),
    ]
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('dairy', 'Dairy'),
        ('grains', 'Grains'),
        ('other', 'Other'),
    ]
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price for the smallest variation
    variation = models.CharField(max_length=10, choices=VARIATION_CHOICES, default='1kg')
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

    @property
    def price(self):
        # Calculate the price based on the variation
        if self.variation == '1L':
            return self.base_price
        elif self.variation == '2L':
            return self.base_price * 2
        elif self.variation == '1kg':
            return self.base_price
        elif self.variation == '2kg':
            return self.base_price * 2
        return self.base_price


class Notification(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message