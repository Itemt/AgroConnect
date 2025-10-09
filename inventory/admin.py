from django.contrib import admin
from .models import Crop

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'productor', 'cantidad_estimada', 'unidad_medida', 'estado', 'fecha_disponibilidad')
    list_filter = ('categoria', 'estado', 'productor')
    search_fields = ('nombre', 'productor__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Información del Cultivo', {
            'fields': ('nombre', 'categoria', 'productor')
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