from django.contrib import admin
from .models import Product, Crop

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'descripcion')
        }),
    )

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'productor', 'estado', 'cantidad_estimada', 'unidad_medida', 'fecha_disponibilidad')
    list_filter = ('estado', 'unidad_medida', 'fecha_disponibilidad')
    search_fields = ('nombre_producto', 'productor__first_name', 'productor__last_name')
    raw_id_fields = ('productor',)
    date_hierarchy = 'fecha_disponibilidad'
    list_editable = ('estado',)
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre_producto', 'productor')
        }),
        ('Detalles de Producción', {
            'fields': ('cantidad_estimada', 'unidad_medida', 'estado', 'fecha_disponibilidad')
        }),
        ('Información Adicional', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('productor')

# Acciones personalizadas
@admin.action(description='Marcar cultivos como listos para cosecha')
def mark_ready_for_harvest(modeladmin, request, queryset):
    updated = queryset.update(estado='listo_cosecha')
    modeladmin.message_user(request, f'{updated} cultivos marcados como listos para cosecha.')

@admin.action(description='Marcar cultivos como cosechados')
def mark_harvested(modeladmin, request, queryset):
    updated = queryset.update(estado='cosechado')
    modeladmin.message_user(request, f'{updated} cultivos marcados como cosechados.')

CropAdmin.actions = [mark_ready_for_harvest, mark_harvested]