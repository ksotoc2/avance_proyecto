import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from prestamos.models import Prestamo, Devolucion
from libros.models import Libro
from prestamos.services import actualizar_stock

class Command(BaseCommand):
    help = 'Crea préstamos y devoluciones de prueba'

    def add_arguments(self, parser):
        parser.add_argument('--prestamos', type=int, default=30, help='Número de préstamos a crear')
        parser.add_argument('--porcentaje_devueltos', type=int, default=60, 
                           help='Porcentaje de préstamos que serán devueltos (0-100)')
        parser.add_argument('--porcentaje_retrasados', type=int, default=20, 
                           help='Porcentaje de préstamos activos que estarán retrasados (0-100)')

    def handle(self, *args, **options):
        # Verificar que existan usuarios y libros
        docentes = User.objects.filter(perfil__cargo='docente')
        libros_disponibles = Libro.objects.filter(stock__gt=0)
        
        if not docentes.exists():
            self.stdout.write(self.style.ERROR('No hay docentes en la base de datos. Ejecuta primero seed_usuarios.'))
            return
        
        if not libros_disponibles.exists():
            self.stdout.write(self.style.ERROR('No hay libros con stock disponible. Ejecuta primero seed_libros.'))
            return
        
        # Crear préstamos
        prestamos_creados = []
        intentos = 0
        max_intentos = options['prestamos'] * 2  # Permitir más intentos que préstamos solicitados
        
        while len(prestamos_creados) < options['prestamos'] and intentos < max_intentos:
            intentos += 1
            
            # Seleccionar un docente aleatorio
            docente = random.choice(docentes)
            
            # Seleccionar un libro aleatorio CON STOCK DISPONIBLE
            libros_con_stock = Libro.objects.filter(stock__gt=0)
            if not libros_con_stock.exists():
                self.stdout.write(self.style.WARNING('No quedan libros con stock disponible.'))
                break
                
            libro = random.choice(libros_con_stock)
            
            # Fechas aleatorias en los últimos 90 días
            dias_atras = random.randint(1, 90)
            fecha_prestamo = timezone.now() - timedelta(days=dias_atras)
            fecha_devolucion = fecha_prestamo.date() + timedelta(days=15)  # 15 días de préstamo
            
            try:
                # Crear préstamo
                prestamo = Prestamo.objects.create(
                    usuario=docente,
                    libro=libro,
                    fecha_prestamo=fecha_prestamo,
                    fecha_devolucion_esperada=fecha_devolucion,
                    estado='activo'
                )
                
                # El stock ya se actualiza en el método save() del modelo Prestamo
                # No necesitamos actualizarlo manualmente aquí
                
                prestamos_creados.append(prestamo)
                self.stdout.write(self.style.SUCCESS(f'Préstamo creado: {prestamo}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al crear préstamo: {e}'))
                continue
        
        if len(prestamos_creados) < options['prestamos']:
            self.stdout.write(self.style.WARNING(
                f'Solo se pudieron crear {len(prestamos_creados)} préstamos de los {options["prestamos"]} solicitados '
                f'debido a limitaciones de stock.'
            ))
        
        # Determinar cuántos préstamos serán devueltos
        num_devueltos = int(len(prestamos_creados) * options['porcentaje_devueltos'] / 100)
        prestamos_a_devolver = random.sample(prestamos_creados, min(num_devueltos, len(prestamos_creados)))
        
        # Crear devoluciones
        for prestamo in prestamos_a_devolver:
            # Determinar si la devolución fue a tiempo o con retraso
            dias_retraso = random.randint(-5, 10)  # Negativo: anticipado, Positivo: retrasado
            fecha_devolucion = prestamo.fecha_devolucion_esperada + timedelta(days=dias_retraso)
            
            # Asegurar que la fecha de devolución no sea en el futuro
            if fecha_devolucion > timezone.now().date():
                fecha_devolucion = timezone.now().date()
            
            # Estado del libro al devolverlo
            estados_libro = ['bueno', 'dañado', 'perdido']
            pesos = [0.85, 0.10, 0.05]  # 85% bueno, 10% dañado, 5% perdido
            estado_libro = random.choices(estados_libro, weights=pesos, k=1)[0]
            
            try:
                # Crear devolución
                devolucion = Devolucion.objects.create(
                    prestamo=prestamo,
                    fecha_devolucion=fecha_devolucion,
                    estado_libro=estado_libro,
                    observacion=f"Devolución de prueba - Estado: {estado_libro}"
                )
                
                self.stdout.write(self.style.SUCCESS(f'Devolución creada: {devolucion}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al crear devolución: {e}'))
        
        # Marcar algunos préstamos activos como retrasados
        prestamos_activos = [p for p in prestamos_creados if p not in prestamos_a_devolver]
        num_retrasados = int(len(prestamos_activos) * options['porcentaje_retrasados'] / 100)
        
        for prestamo in random.sample(prestamos_activos, min(num_retrasados, len(prestamos_activos))):
            # Establecer fecha de devolución en el pasado
            prestamo.fecha_devolucion_esperada = timezone.now().date() - timedelta(days=random.randint(1, 30))
            prestamo.estado = 'retrasado'
            prestamo.save()
            self.stdout.write(self.style.SUCCESS(f'Préstamo marcado como retrasado: {prestamo}'))
        
        self.stdout.write(self.style.SUCCESS(f'Creados {len(prestamos_creados)} préstamos y {len(prestamos_a_devolver)} devoluciones'))
