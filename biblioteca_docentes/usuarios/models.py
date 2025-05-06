from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    CARGO_CHOICES = [
        ('docente', 'Docente'),
        ('bibliotecario', 'Bibliotecario'),
        ('director', 'Director Académico'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES, default='docente')
    departamento = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_cargo_display()}"
    
    def es_bibliotecario(self):
        return self.cargo == 'bibliotecario'
    
    def es_docente(self):
        return self.cargo == 'docente'
    
    def es_director(self):
        return self.cargo == 'director'

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()
