from django.db import models
from django.conf import settings
import os

class CategoriaLibro(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Categoría de Libro'
        verbose_name_plural = 'Categorías de Libros'
    
    def __str__(self):
        return self.nombre

def libro_portada_path(instance, filename):
    # El archivo se subirá a MEDIA_ROOT/portadas/libro_<id>/<filename>
    return f'portadas/libro_{instance.isbn}/{filename}'

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    editorial = models.CharField(max_length=100)
    isbn = models.CharField('ISBN', max_length=20, unique=True)
    stock = models.PositiveIntegerField(default=1)
    categoria = models.ForeignKey(CategoriaLibro, on_delete=models.PROTECT, related_name='libros')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    portada = models.ImageField(upload_to=libro_portada_path, blank=True, null=True, verbose_name='Imagen de Portada')
    
    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        ordering = ['titulo']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"
    
    def disponible(self):
        return self.stock > 0
    
    def delete(self, *args, **kwargs):
        # Eliminar la imagen de portada si existe
        if self.portada:
            if os.path.isfile(self.portada.path):
                os.remove(self.portada.path)
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        # Si se está actualizando el libro y cambiando la imagen
        if self.pk:
            try:
                old_instance = Libro.objects.get(pk=self.pk)
                if old_instance.portada and self.portada != old_instance.portada:
                    if os.path.isfile(old_instance.portada.path):
                        os.remove(old_instance.portada.path)
            except Libro.DoesNotExist:
                pass
        super().save(*args, **kwargs)
