from django.contrib import admin
from .models import Product, Crop

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('product', 'producer', 'status', 'estimated_quantity', 'unit', 'estimated_availability_date')
    list_filter = ('status', 'estimated_availability_date')
    search_fields = ('product__name', 'producer__first_name', 'producer__last_name')
    raw_id_fields = ('producer',)
    date_hierarchy = 'estimated_availability_date'
    list_editable = ('status',)
    
    fieldsets = (
        ('Información del Cultivo', {
            'fields': ('producer', 'product', 'status')
        }),
        ('Detalles de Producción', {
            'fields': ('estimated_quantity', 'unit', 'estimated_availability_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'producer')

# Acciones personalizadas
@admin.action(description='Marcar cultivos como listos para cosechar')
def mark_ready_for_harvest(modeladmin, request, queryset):
    updated = queryset.update(status='listo para cosechar')
    modeladmin.message_user(request, f'{updated} cultivos marcados como listos para cosechar.')

@admin.action(description='Marcar cultivos como cosechados')
def mark_harvested(modeladmin, request, queryset):
    updated = queryset.update(status='cosechado')
    modeladmin.message_user(request, f'{updated} cultivos marcados como cosechados.')

CropAdmin.actions = [mark_ready_for_harvest, mark_harvested]