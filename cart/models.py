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
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unidad_compra = models.CharField(max_length=20, default='kg', verbose_name="Unidad de Compra")

    def __str__(self):
        return f'{self.quantity} {self.unidad_compra} de {self.publication.cultivo.nombre}'

    @property
    def get_item_price(self):
        """Calcula el precio total con conversión de unidades si es necesario"""
        # Si la unidad de compra es diferente a la unidad de venta, convertir
        if self.unidad_compra != self.publication.unidad_medida:
            precio_convertido = self.publication.obtener_precio_en_unidad(self.unidad_compra)
            if precio_convertido is None:
                # Si no se puede convertir, usar precio original
                return self.publication.precio_por_unidad * self.quantity
            return precio_convertido * float(self.quantity)
        return self.publication.precio_por_unidad * float(self.quantity)
    
    @property
    def precio_unitario_display(self):
        """Retorna el precio por unidad en la unidad de compra"""
        if self.unidad_compra != self.publication.unidad_medida:
            precio_convertido = self.publication.obtener_precio_en_unidad(self.unidad_compra)
            if precio_convertido is not None:
                return precio_convertido
        return self.publication.precio_por_unidad
