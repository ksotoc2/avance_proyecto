from django.contrib import admin
from .models import Prestamo, Devolucion
from libros.models import Libro, CategoriaLibro
import csv
from django.http import HttpResponse

class DevolucionInline(admin.StackedInline):
    model = Devolucion
    can_delete = False
    extra = 0

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('libro', 'usuario', 'get_departamento', 'fecha_prestamo', 'fecha_devolucion_esperada', 'estado', 'dias_retraso')
    list_filter = ('estado', 'fecha_prestamo', 'fecha_devolucion_esperada', 'usuario__perfil__departamento')
    search_fields = ('libro__titulo', 'usuario__username', 'usuario__first_name', 'usuario__last_name')
    date_hierarchy = 'fecha_prestamo'
    inlines = [DevolucionInline]
    readonly_fields = ('fecha_prestamo',)
    
    def get_departamento(self, obj):
        return obj.usuario.perfil.departamento
    get_departamento.short_description = 'Departamento'
    get_departamento.admin_order_field = 'usuario__perfil__departamento'
    
    def dias_retraso(self, obj):
        dias = obj.dias_retraso()
        if dias > 0:
            return f"{dias} días"
        return "0"
    dias_retraso.short_description = 'Días de retraso'
    
    actions = ['marcar_como_devuelto', 'exportar_a_csv']
    
    def marcar_como_devuelto(self, request, queryset):
        for prestamo in queryset.filter(estado='activo'):
            Devolucion.objects.create(prestamo=prestamo)
        self.message_user(request, f"{queryset.count()} préstamos marcados como devueltos.")
    marcar_como_devuelto.short_description = "Marcar préstamos seleccionados como devueltos"
    
    def exportar_a_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="prestamos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Libro', 'Usuario', 'Departamento', 'Fecha Préstamo', 'Fecha Devolución Esperada', 'Estado', 'Días Retraso'])
        
        for prestamo in queryset:
            writer.writerow([
                prestamo.libro.titulo,
                prestamo.usuario.get_full_name(),
                prestamo.usuario.perfil.departamento,
                prestamo.fecha_prestamo.strftime('%Y-%m-%d'),
                prestamo.fecha_devolucion_esperada.strftime('%Y-%m-%d'),
                prestamo.get_estado_display(),
                prestamo.dias_retraso(),
            ])
        
        return response
    exportar_a_csv.short_description = "Exportar préstamos seleccionados a CSV"

@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ('prestamo', 'fecha_devolucion', 'estado_libro', 'observacion')
    list_filter = ('estado_libro', 'fecha_devolucion')
    search_fields = ('prestamo__libro__titulo', 'prestamo__usuario__username')
    date_hierarchy = 'fecha_devolucion'
