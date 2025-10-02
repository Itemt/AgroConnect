from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ProducerProfile, BuyerProfile

class ProducerProfileInline(admin.StackedInline):
    model = ProducerProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Productor'
    fields = ('location', 'farm_description', 'main_crops')

class BuyerProfileInline(admin.StackedInline):
    model = BuyerProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Comprador'
    fields = ('company_name', 'business_type')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'role', 'password', 'password2'),
        }),
    )
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        
        inlines = []
        if obj.role == 'Productor':
            inlines.append(ProducerProfileInline(self.model, self.admin_site))
        elif obj.role == 'Comprador':
            inlines.append(BuyerProfileInline(self.model, self.admin_site))
        
        # Llama al método de la superclase para incluir cualquier inline predeterminado
        base_inlines = super().get_inline_instances(request, obj)
        return inlines + base_inlines

@admin.register(ProducerProfile)
class ProducerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'main_crops')
    search_fields = ('user__first_name', 'user__last_name', 'location')
    raw_id_fields = ('user',)

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'business_type')
    list_filter = ('business_type',)
    search_fields = ('user__first_name', 'user__last_name', 'company_name')
    raw_id_fields = ('user',)

# Personalizar el sitio de administración
admin.site.site_header = 'AgroConnect Administración'
admin.site.site_title = 'AgroConnect Admin'
admin.site.index_title = 'Panel de Control'