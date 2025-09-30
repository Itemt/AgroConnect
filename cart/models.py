from django.db import models
from django.conf import settings
from marketplace.models import Publication

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.username}'

    @property
    def get_total_price(self):
        total = sum(item.get_item_price for item in self.items.all())
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.publication.cultivo.nombre_producto}'

    @property
    def get_item_price(self):
        return self.publication.precio_por_unidad * self.quantity
