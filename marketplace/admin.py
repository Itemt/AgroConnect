from django.contrib import admin
from django.utils.html import format_html
from .models import Publication, PublicationImage


class PublicationImageInline(admin.TabularInline):
    """Inline para gestionar imágenes de publicación"""
    model = PublicationImage
    extra = 1
    max_num = 10
    fields = ('image', 'is_primary', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista Previa'


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('cultivo_info', 'productor_info', 'precio_por_unidad', 'cantidad_disponible', 'estado', 'estado_badge', 'created_at')
    list_filter = ('estado', 'created_at')
    search_fields = ('cultivo__nombre', 'cultivo__productor__first_name', 'cultivo__productor__last_name')
    list_editable = ('estado',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    raw_id_fields = ('cultivo',)
    inlines = [PublicationImageInline]
    
    fieldsets = (
        ('Información del Cultivo', {
            'fields': ('cultivo',)
        }),
        ('Detalles de Venta', {
            'fields': ('precio_por_unidad', 'cantidad_disponible', 'cantidad_minima')
        }),
        ('Descripción y Estado', {
            'fields': ('descripcion', 'estado')
        }),
    )
    
    def cultivo_info(self, obj):
        return f"{obj.cultivo.nombre} ({obj.cultivo.cantidad_estimada} {obj.cultivo.unidad_medida})"
    cultivo_info.short_description = 'Cultivo'
    
    def productor_info(self, obj):
        return f"{obj.cultivo.productor.first_name} {obj.cultivo.productor.last_name}"
    productor_info.short_description = 'Productor'
    
    def estado_badge(self, obj):
        colors = {
            'disponible': 'green',
            'vendido': 'orange',
            'pausado': 'blue',
            'agotado': 'red',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado Visual'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cultivo__productor')

# Acciones personalizadas
@admin.action(description='Marcar publicaciones como disponibles')
def mark_available(modeladmin, request, queryset):
    updated = queryset.update(estado='disponible')
    modeladmin.message_user(request, f'{updated} publicaciones marcadas como disponibles.')

@admin.action(description='Marcar publicaciones como vendidas')
def mark_sold(modeladmin, request, queryset):
    updated = queryset.update(estado='vendido')
    modeladmin.message_user(request, f'{updated} publicaciones marcadas como vendidas.')

@admin.action(description='Pausar publicaciones')
def pause_publications(modeladmin, request, queryset):
    updated = queryset.update(estado='pausado')
    modeladmin.message_user(request, f'{updated} publicaciones pausadas.')

PublicationAdmin.actions = [mark_available, mark_sold, pause_publications]