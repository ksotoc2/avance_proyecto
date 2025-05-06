from django.utils import timezone

def verificar_stock(libro):
    """Verifica si hay ejemplares disponibles del libro."""
    return libro.stock > 0

def actualizar_stock(libro, cantidad):
    """Aumenta o disminuye el stock del libro."""
    libro.stock += cantidad
    libro.save()
    return libro.stock

def calcular_dias_retraso(prestamo):
    """Calcula los días de retraso de un préstamo."""
    if prestamo.estado == 'devuelto':
        try:
            devolucion = prestamo.devolucion
            if devolucion.fecha_devolucion > prestamo.fecha_devolucion_esperada:
                return (devolucion.fecha_devolucion - prestamo.fecha_devolucion_esperada).days
        except:
            return 0
    elif prestamo.estado in ['activo', 'retrasado']:
        hoy = timezone.now().date()
        if hoy > prestamo.fecha_devolucion_esperada:
            return (hoy - prestamo.fecha_devolucion_esperada).days
    return 0

def actualizar_estado_prestamo(prestamo):
    """Actualiza el estado del préstamo según las condiciones."""
    # Si ya está devuelto o perdido, no hacer nada
    if prestamo.estado in ['devuelto', 'perdido']:
        return prestamo
    
    # Verificar si está retrasado
    dias_retraso = calcular_dias_retraso(prestamo)
    if dias_retraso > 0 and prestamo.estado == 'activo':
        prestamo.estado = 'retrasado'
        prestamo.save()
    
    return prestamo
