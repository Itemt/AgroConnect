from django.db import models
from core.models import BaseModel
from inventory.models import Crop

# Create your models here.

class Publication(BaseModel):
    STATUS_CHOICES = (
        ('disponible', 'Disponible'),
        ('vendido', 'Vendido'),
        ('caducado', 'Caducado'),
    )
    crop = models.OneToOneField(Crop, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponible')

    def __str__(self):
        return f'Publication for {self.crop}'
