from django.contrib import admin
from .models import CategoriaLibro, Libro
from django.utils.html import format_html

@admin.register(CategoriaLibro)
class CategoriaLibroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'editorial', 'isbn', 'stock', 'categoria', 'disponible', 'mostrar_portada')
    list_filter = ('categoria', 'editorial')
    search_fields = ('titulo', 'autor', 'isbn')
    list_editable = ('stock',)
    readonly_fields = ('mostrar_portada_grande',)
    fieldsets = (
        (None, {
            'fields': ('titulo', 'autor', 'editorial', 'isbn', 'stock', 'categoria')
        }),
        ('Portada', {
            'fields': ('portada', 'mostrar_portada_grande'),
            'classes': ('collapse',),
        }),
    )
    
    def disponible(self, obj):
        return obj.stock > 0
    disponible.boolean = True
    disponible.short_description = 'Disponible'
    
    def mostrar_portada(self, obj):
        if obj.portada:
            return format_html('<img src="{}" width="50" height="70" style="object-fit: cover; border-radius: 5px;" />', obj.portada.url)
        return format_html('<span class="text-muted">Sin portada</span>')
    mostrar_portada.short_description = 'Portada'
    
    def mostrar_portada_grande(self, obj):
        if obj.portada:
            return format_html('<img src="{}" width="200" height="280" style="object-fit: cover; border-radius: 10px;" />', obj.portada.url)
        return format_html('<div style="width: 200px; height: 280px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; border-radius: 10px; border: 1px dashed #dee2e6;"><span class="text-muted">Sin imagen de portada</span></div>')
    mostrar_portada_grande.short_description = 'Vista previa'
