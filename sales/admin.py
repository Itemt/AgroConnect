from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, Order

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender', 'content', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'publication_info', 'participants_info', 'message_count', 'last_updated')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('publication__crop__product__name', 'participants__first_name', 'participants__last_name')
    inlines = [MessageInline]
    
    def publication_info(self, obj):
        return f"{obj.publication.crop.product.name} - {obj.publication.crop.producer.first_name}"
    publication_info.short_description = 'Publicación'
    
    def participants_info(self, obj):
        participants = obj.participants.all()
        return ", ".join([f"{p.first_name} {p.last_name}" for p in participants])
    participants_info.short_description = 'Participantes'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Mensajes'
    
    def last_updated(self, obj):
        return obj.updated_at.strftime('%d/%m/%Y %H:%M')
    last_updated.short_description = 'Última Actualización'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('publication__crop__product', 'publication__crop__producer').prefetch_related('participants', 'messages')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation_info', 'sender', 'content_preview', 'created_at')
    list_filter = ('created_at', 'sender__role')
    search_fields = ('content', 'sender__first_name', 'sender__last_name')
    readonly_fields = ('created_at',)
    
    def conversation_info(self, obj):
        return f"Conversación #{obj.conversation.id}"
    conversation_info.short_description = 'Conversación'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenido'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'sender')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'publication_info', 'buyer_info', 'agreed_quantity', 'final_price', 'status', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('publication__crop__product__name', 'buyer__first_name', 'buyer__last_name')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('publication', 'buyer')
        }),
        ('Detalles del Pedido', {
            'fields': ('agreed_quantity', 'final_price', 'status')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def publication_info(self, obj):
        return f"{obj.publication.crop.product.name} - {obj.publication.crop.producer.first_name}"
    publication_info.short_description = 'Publicación'
    
    def buyer_info(self, obj):
        return f"{obj.buyer.first_name} {obj.buyer.last_name}"
    buyer_info.short_description = 'Comprador'
    
    def status_badge(self, obj):
        colors = {
            'acordado': 'blue',
            'en tránsito': 'orange',
            'entregado': 'green',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('publication__crop__product', 'publication__crop__producer', 'buyer')

# Acciones personalizadas
@admin.action(description='Marcar pedidos como en tránsito')
def mark_in_transit(modeladmin, request, queryset):
    updated = queryset.update(status='en tránsito')
    modeladmin.message_user(request, f'{updated} pedidos marcados como en tránsito.')

@admin.action(description='Marcar pedidos como entregados')
def mark_delivered(modeladmin, request, queryset):
    updated = queryset.update(status='entregado')
    modeladmin.message_user(request, f'{updated} pedidos marcados como entregados.')

OrderAdmin.actions = [mark_in_transit, mark_delivered]