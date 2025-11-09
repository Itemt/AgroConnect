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
        return round(total, 2)

    @property
    def has_invalid_items(self):
        """Retorna True si algún item supera disponibilidad"""
        for item in self.items.all():
            if item.is_over_available:
                return True
        return False

    @property
    def totals_by_unit(self):
        """Suma de cantidades agrupadas por unidad de compra en el carrito"""
        totals = {}
        for item in self.items.all():
            unit = item.unidad_compra
            totals[unit] = totals.get(unit, 0.0) + float(item.quantity)
        # Redondear a 1 decimal
        return {u: round(q, 1) for u, q in totals.items()}

    @property
    def totals_by_unit_items(self):
        """Lista [(unidad, cantidad)] útil para plantillas, ordenada por nombre de unidad"""
        totals = self.totals_by_unit
        return sorted(totals.items(), key=lambda x: x[0])

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
                return float(self.publication.precio_por_unidad) * float(self.quantity)
            return precio_convertido * float(self.quantity)
        return float(self.publication.precio_por_unidad) * float(self.quantity)
    
    @property
    def precio_unitario_display(self):
        """Retorna el precio por unidad en la unidad de compra"""
        if self.unidad_compra != self.publication.unidad_medida:
            precio_convertido = self.publication.obtener_precio_en_unidad(self.unidad_compra)
            if precio_convertido is not None:
                return precio_convertido
        return float(self.publication.precio_por_unidad)

    @property
    def minimo_en_unidad_compra(self):
        """Cantidad mínima de venta convertida a la unidad de compra del carrito"""
        if self.unidad_compra == self.publication.unidad_medida:
            return float(self.publication.cantidad_minima)
        cantidad = self.publication.convertir_unidad(
            self.publication.cantidad_minima,
            self.publication.unidad_medida,
            self.unidad_compra,
        )
        # Si no es convertible, al menos 1
        return float(cantidad) if cantidad is not None else 1.0

    @property
    def disponible_en_unidad_compra(self):
        """Cantidad disponible convertida a la unidad de compra del carrito"""
        if self.unidad_compra == self.publication.unidad_medida:
            return float(self.publication.cantidad_disponible)
        cantidad = self.publication.convertir_unidad(
            self.publication.cantidad_disponible,
            self.publication.unidad_medida,
            self.unidad_compra,
        )
        return float(cantidad) if cantidad is not None else float(self.publication.cantidad_disponible)

    @property
    def is_below_minimum(self):
        """Siempre retorna False - no hay mínimos de compra"""
        return False

    @property
    def is_over_available(self):
        """True si la cantidad actual supera la disponibilidad en la unidad de compra"""
        try:
            return float(self.quantity) - 1e-9 > float(self.disponible_en_unidad_compra)
        except Exception:
            return False

    @property
    def validation_error(self):
        """Mensaje de error amigable si el item es inválido, sino cadena vacía"""
        if self.is_over_available:
            return f"Disponible: {float(self.disponible_en_unidad_compra):.1f} {self.unidad_compra}"
        return ""