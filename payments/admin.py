from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'epayco_ref',
        'order',
        'user',
        'amount',
        'currency',
        'payment_method',
        'status',
        'created_at',
        'paid_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = [
        'epayco_ref',
        'epayco_transaction_id',
        'user__username',
        'user__email',
        'order__id'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'epayco_ref',
        'epayco_transaction_id',
        'response_data'
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': ('order', 'user', 'status')
        }),
        ('Detalles del Pago', {
            'fields': ('amount', 'currency', 'payment_method', 'description')
        }),
        ('Información de ePayco', {
            'fields': ('epayco_ref', 'epayco_transaction_id', 'response_data')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir crear pagos manualmente"""
        return False
