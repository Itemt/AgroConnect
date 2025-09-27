from django.db import models
from django.conf import settings
from core.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Crop(BaseModel):
    STATUS_CHOICES = (
        ('en crecimiento', 'En crecimiento'),
        ('listo para cosechar', 'Listo para cosechar'),
        ('cosechado', 'Cosechado'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crops')
    estimated_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20) # e.g., kg, ton, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    estimated_availability_date = models.DateField()

    def __str__(self):
        return f'{self.estimated_quantity} {self.unit} of {self.product.name} from {self.producer.username}'
