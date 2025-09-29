from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, Order, Rating

# Inlines
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'created_at')
    fields = ('sender', 'content', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender')

# Conversation Admin
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'publication_info', 'participants_list', 'created_at')
    list_filter = ('created_at', 'publication__cultivo__nombre_producto')
    search_fields = ('publicacion__cultivo__nombre_producto', 'participants__first_name', 'participants__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    
    def publication_info(self, obj):
        return f"{obj.publication.cultivo.nombre_producto} - {obj.publication.cultivo.productor.first_name}"
    publication_info.short_description = 'Publicación'
    
    def participants_list(self, obj):
        participants = obj.participants.all()
        return ", ".join([f"{p.first_name} {p.last_name}" for p in participants])
    participants_list.short_description = 'Participantes'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('publicacion__cultivo__productor').prefetch_related('participants', 'messages')

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation_info', 'sender', 'content_preview', 'created_at')
    list_filter = ('created_at', 'sender__role')
    search_fields = ('content', 'sender__first_name', 'sender__last_name')
    readonly_fields = ('created_at',)
    
    def conversation_info(self, obj):
        return f"Conversación #{obj.conversation.id}"
    conversation_info.short_description = 'Conversación'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenido'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'sender')

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'publicacion_info', 'comprador_info', 'cantidad_acordada', 'precio_total', 'estado', 'estado_badge', 'created_at')
    list_filter = ('estado', 'created_at', 'publicacion__cultivo__nombre_producto')
    search_fields = ('publicacion__cultivo__nombre_producto', 'comprador__first_name', 'comprador__last_name')
    readonly_fields = ('created_at', 'updated_at', 'fecha_confirmacion', 'fecha_envio', 'fecha_recepcion')
    list_editable = ('estado',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('publicacion', 'comprador', 'cantidad_acordada', 'precio_total')
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_confirmacion', 'fecha_envio', 'fecha_entrega_estimada', 'fecha_recepcion')
        }),
        ('Información de Entrega', {
            'fields': ('direccion_entrega',)
        }),
        ('Notas', {
            'fields': ('notas_comprador', 'notas_vendedor'),
            'classes': ('collapse',)
        }),
        ('Fechas del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def publicacion_info(self, obj):
        return f"{obj.publicacion.cultivo.nombre_producto} - {obj.publicacion.cultivo.productor.first_name}"
    publicacion_info.short_description = 'Publicación'
    
    def comprador_info(self, obj):
        return f"{obj.comprador.first_name} {obj.comprador.last_name}"
    comprador_info.short_description = 'Comprador'
    
    def estado_badge(self, obj):
        colors = {
            'pendiente': '#ffc107',
            'confirmado': '#17a2b8',
            'en_preparacion': '#6f42c1',
            'enviado': '#fd7e14',
            'en_transito': '#20c997',
            'entregado': '#28a745',
            'recibido': '#007bff',
            'completado': '#28a745',
            'cancelado': '#dc3545',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado Visual'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('publicacion__cultivo__productor', 'comprador')

# Rating Admin
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_info', 'calificador', 'calificado', 'calificacion_general', 'promedio_display', 'recomendaria', 'created_at')
    list_filter = ('calificacion_general', 'recomendaria', 'tipo', 'created_at')
    search_fields = ('calificador__first_name', 'calificado__first_name', 'comentario')
    readonly_fields = ('created_at', 'updated_at', 'promedio_calificacion')
    
    fieldsets = (
        ('Información del Rating', {
            'fields': ('pedido', 'calificador', 'calificado', 'tipo')
        }),
        ('Calificaciones', {
            'fields': ('calificacion_general', 'calificacion_comunicacion', 'calificacion_puntualidad', 'calificacion_calidad', 'promedio_calificacion')
        }),
        ('Comentarios y Recomendación', {
            'fields': ('comentario', 'recomendaria')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pedido_info(self, obj):
        return f"Pedido #{obj.pedido.id} - {obj.pedido.publicacion.cultivo.nombre_producto}"
    pedido_info.short_description = 'Pedido'
    
    def promedio_display(self, obj):
        return f"{obj.promedio_calificacion:.1f}/5"
    promedio_display.short_description = 'Promedio'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pedido__publicacion__cultivo', 'calificador', 'calificado')

# Acciones personalizadas para Order
@admin.action(description='Confirmar pedidos seleccionados')
def confirm_orders(modeladmin, request, queryset):
    updated = queryset.filter(estado='pendiente').update(estado='confirmado')
    modeladmin.message_user(request, f'{updated} pedidos confirmados.')

@admin.action(description='Marcar como enviados')
def mark_as_shipped(modeladmin, request, queryset):
    updated = queryset.filter(estado__in=['confirmado', 'en_preparacion']).update(estado='enviado')
    modeladmin.message_user(request, f'{updated} pedidos marcados como enviados.')

@admin.action(description='Marcar como entregados')
def mark_as_delivered(modeladmin, request, queryset):
    updated = queryset.filter(estado__in=['enviado', 'en_transito']).update(estado='entregado')
    modeladmin.message_user(request, f'{updated} pedidos marcados como entregados.')

# Agregar acciones al OrderAdmin
OrderAdmin.actions = [confirm_orders, mark_as_shipped, mark_as_delivered]