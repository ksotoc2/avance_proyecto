from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_cargo', 'get_departamento', 'is_staff')
    list_filter = ('perfil__cargo', 'perfil__departamento', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'perfil__departamento')
    
    def get_cargo(self, obj):
        return obj.perfil.get_cargo_display()
    get_cargo.short_description = 'Cargo'
    get_cargo.admin_order_field = 'perfil__cargo'
    
    def get_departamento(self, obj):
        return obj.perfil.departamento
    get_departamento.short_description = 'Departamento'
    get_departamento.admin_order_field = 'perfil__departamento'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
