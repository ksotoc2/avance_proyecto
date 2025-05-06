from django.db import models
from django.contrib.auth.models import User
from libros.models import Libro
from django.utils import timezone
from datetime import timedelta

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('retrasado', 'Retrasado'),
        ('devuelto', 'Devuelto'),
        ('perdido', 'Perdido'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prestamos')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos')
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-fecha_prestamo']
    
    def __str__(self):
        return f"{self.libro.titulo} - {self.usuario.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Si es un nuevo préstamo, establecer fecha de devolución esperada a 15 días
        if not self.pk and not self.fecha_devolucion_esperada:
            self.fecha_devolucion_esperada = timezone.now().date() + timedelta(days=15)
        
        # Si es un nuevo préstamo, reducir el stock del libro
        if not self.pk:
            self.libro.stock -= 1
            self.libro.save()
        
        super().save(*args, **kwargs)
    
    def dias_retraso(self):
        if self.estado == 'devuelto':
            try:
                devolucion = self.devolucion
                if devolucion.fecha_devolucion > self.fecha_devolucion_esperada:
                    return (devolucion.fecha_devolucion - self.fecha_devolucion_esperada).days
            except Devolucion.DoesNotExist:
                return 0
        elif self.estado in ['activo', 'retrasado']:
            hoy = timezone.now().date()
            if hoy > self.fecha_devolucion_esperada:
                return (hoy - self.fecha_devolucion_esperada).days
        return 0

class Devolucion(models.Model):
    ESTADO_LIBRO_CHOICES = [
        ('bueno', 'Bueno'),
        ('dañado', 'Dañado'),
        ('perdido', 'Perdido'),
    ]
    
    prestamo = models.OneToOneField(Prestamo, on_delete=models.CASCADE, related_name='devolucion')
    fecha_devolucion = models.DateField(default=timezone.now)
    estado_libro = models.CharField(max_length=20, choices=ESTADO_LIBRO_CHOICES, default='bueno')
    observacion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
    
    def __str__(self):
        return f"Devolución de {self.prestamo}"
    
    def save(self, *args, **kwargs):
        # Actualizar el estado del préstamo
        if self.estado_libro == 'perdido':
            self.prestamo.estado = 'perdido'
        else:
            self.prestamo.estado = 'devuelto'
        self.prestamo.save()
        
        # Si el libro no está perdido, aumentar el stock
        if self.estado_libro != 'perdido':
            self.prestamo.libro.stock += 1
            self.prestamo.libro.save()
        
        super().save(*args, **kwargs)
