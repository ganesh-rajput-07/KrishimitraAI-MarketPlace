# admin_panel/models.py
from django.db import models
from django.contrib.auth.models import User

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username