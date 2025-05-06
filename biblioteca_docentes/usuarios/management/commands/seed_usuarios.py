import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles'

    def add_arguments(self, parser):
        parser.add_argument('--docentes', type=int, default=10, help='Número de docentes a crear')
        parser.add_argument('--bibliotecarios', type=int, default=2, help='Número de bibliotecarios a crear')
        parser.add_argument('--directores', type=int, default=1, help='Número de directores a crear')

    def handle(self, *args, **options):
        # Datos de ejemplo
        nombres = ['Juan', 'María', 'Pedro', 'Ana', 'Luis', 'Carla', 'José', 'Laura', 'Carlos', 'Sofía', 
                  'Miguel', 'Lucía', 'Fernando', 'Valentina', 'Javier', 'Gabriela', 'Roberto', 'Patricia']
        
        apellidos = ['García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez', 'Sánchez', 'Ramírez', 
                    'Torres', 'Flores', 'Rivera', 'Gómez', 'Díaz', 'Reyes', 'Cruz', 'Morales', 'Ortiz', 'Ramos']
        
        departamentos = ['Matemáticas', 'Física', 'Química', 'Biología', 'Historia', 'Literatura', 
                        'Informática', 'Ingeniería', 'Economía', 'Derecho', 'Medicina', 'Psicología']

        # Crear superusuario si no existe
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            admin.perfil.cargo = 'bibliotecario'
            admin.perfil.departamento = 'Administración'
            admin.perfil.save()
            self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {admin.username}'))

        # Crear docentes
        for i in range(options['docentes']):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            username = f"{nombre.lower()}.{apellido.lower()}{i}"
            email = f"{username}@example.com"
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=nombre,
                    last_name=apellido
                )
                user.perfil.cargo = 'docente'
                user.perfil.departamento = random.choice(departamentos)
                user.perfil.save()
                self.stdout.write(self.style.SUCCESS(f'Docente creado: {user.username}'))

        # Crear bibliotecarios
        for i in range(options['bibliotecarios']):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            username = f"biblio.{nombre.lower()}{i}"
            email = f"{username}@example.com"
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=nombre,
                    last_name=apellido
                )
                user.perfil.cargo = 'bibliotecario'
                user.perfil.departamento = 'Biblioteca'
                user.perfil.save()
                self.stdout.write(self.style.SUCCESS(f'Bibliotecario creado: {user.username}'))

        # Crear directores
        for i in range(options['directores']):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            username = f"director.{nombre.lower()}{i}"
            email = f"{username}@example.com"
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=nombre,
                    last_name=apellido
                )
                user.perfil.cargo = 'director'
                user.perfil.departamento = 'Dirección Académica'
                user.perfil.save()
                self.stdout.write(self.style.SUCCESS(f'Director creado: {user.username}'))

        self.stdout.write(self.style.SUCCESS('Usuarios creados exitosamente'))
