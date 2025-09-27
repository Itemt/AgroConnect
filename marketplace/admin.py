from django.contrib import admin
from django.utils.html import format_html
from .models import Publication

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('crop_info', 'producer_info', 'price_per_unit', 'available_quantity', 'status', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('crop__product__name', 'crop__producer__first_name', 'crop__producer__last_name')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('crop',)
        }),
        ('Detalles de Venta', {
            'fields': ('price_per_unit', 'available_quantity')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
    )
    
    def crop_info(self, obj):
        return f"{obj.crop.product.name} ({obj.crop.estimated_quantity} {obj.crop.unit})"
    crop_info.short_description = 'Cultivo'
    
    def producer_info(self, obj):
        return f"{obj.crop.producer.first_name} {obj.crop.producer.last_name}"
    producer_info.short_description = 'Productor'
    
    def status_badge(self, obj):
        colors = {
            'disponible': 'green',
            'vendido': 'orange',
            'caducado': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('crop__product', 'crop__producer')

# Acciones personalizadas
@admin.action(description='Marcar publicaciones como disponibles')
def mark_available(modeladmin, request, queryset):
    updated = queryset.update(status='disponible')
    modeladmin.message_user(request, f'{updated} publicaciones marcadas como disponibles.')

@admin.action(description='Marcar publicaciones como vendidas')
def mark_sold(modeladmin, request, queryset):
    updated = queryset.update(status='vendido')
    modeladmin.message_user(request, f'{updated} publicaciones marcadas como vendidas.')

PublicationAdmin.actions = [mark_available, mark_sold]