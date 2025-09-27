from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Productor', 'Productor'),
        ('Comprador', 'Comprador'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)

class ProducerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='producer_profile')
    location = models.CharField(max_length=255)
    farm_description = models.TextField()
    main_crops = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class BuyerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    company_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
