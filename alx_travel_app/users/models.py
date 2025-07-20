# alx_travel_app/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model to allow for future expansion without needing migrations.
    """
    # Add any additional fields here if needed, e.g., phone_number, profile_picture
    # phone_number = models.CharField(max_length=20, blank=True, null=True)
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username