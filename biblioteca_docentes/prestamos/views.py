from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Prestamo, Devolucion
from .forms import PrestamoForm, DevolucionForm
from libros.models import Libro
from usuarios.models import PerfilUsuario
from .services import verificar_stock, actualizar_stock, calcular_dias_retraso, actualizar_estado_prestamo

@login_required
def dashboard(request):
    # Verificar el rol del usuario
    perfil = request.user.perfil
    
    if perfil.es_docente():
        # Para docentes, mostrar sus préstamos activos
        prestamos_activos = Prestamo.objects.filter(
            usuario=request.user,
            estado__in=['activo', 'retrasado']
        )
        
        # Actualizar estados de préstamos
        for prestamo in prestamos_activos:
            actualizar_estado_prestamo(prestamo)
        
        context = {
            'prestamos_activos': prestamos_activos,
            'total_activos': prestamos_activos.count(),
            'total_retrasados': prestamos_activos.filter(estado='retrasado').count(),
        }
        return render(request, 'prestamos/dashboard_docente.html', context)
    
    elif perfil.es_bibliotecario() or perfil.es_director():
        # Para bibliotecarios y directores, mostrar estadísticas generales
        prestamos_activos = Prestamo.objects.filter(estado__in=['activo', 'retrasado'])
        prestamos_retrasados = prestamos_activos.filter(estado='retrasado')
        
        # Actualizar estados de préstamos
        for prestamo in prestamos_activos:
            actualizar_estado_prestamo(prestamo)
        
        context = {
            'total_prestamos_activos': prestamos_activos.count(),
            'total_prestamos_retrasados': prestamos_retrasados.count(),
            'prestamos_recientes': Prestamo.objects.all().order_by('-fecha_prestamo')[:5],
            'devoluciones_recientes': Devolucion.objects.all().order_by('-fecha_devolucion')[:5],
        }
        return render(request, 'prestamos/dashboard_admin.html', context)
    
    # Si no tiene un rol definido
    return render(request, 'prestamos/dashboard_error.html')

@login_required
def registrar_prestamo(request):
    # Solo bibliotecarios pueden registrar préstamos
    if not request.user.perfil.es_bibliotecario():
        messages.error(request, "No tienes permisos para registrar préstamos.")
        return redirect('dashboard')
    
    # Obtener libro preseleccionado de la URL si existe
    initial_data = {}
    libro_id = request.GET.get('libro')
    if libro_id:
        try:
            libro = Libro.objects.get(id=libro_id)
            initial_data['libro'] = libro.id
            
            # Verificar si hay stock disponible
            if not verificar_stock(libro):
                messages.error(request, f"No hay ejemplares disponibles de {libro.titulo}.")
                return redirect('detalle_libro', libro_id=libro.id)
        except Libro.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = PrestamoForm(request.POST, usuario_actual=request.user, initial=initial_data)
        if form.is_valid():
            prestamo = form.save(commit=False)
            
            # Verificar si el docente ya tiene este libro prestado
            prestamo_existente = Prestamo.objects.filter(
                usuario=prestamo.usuario,
                libro=prestamo.libro,
                estado__in=['activo', 'retrasado']
            ).exists()
            
            if prestamo_existente:
                messages.error(request, f"El docente {prestamo.usuario.get_full_name()} ya tiene prestado el libro {prestamo.libro.titulo}.")
                return redirect('registrar_prestamo')
            
            # Verificar stock
            if not verificar_stock(prestamo.libro):
                messages.error(request, f"No hay ejemplares disponibles de {prestamo.libro.titulo}.")
                return redirect('registrar_prestamo')
            
            prestamo.save()
            messages.success(request, "Préstamo registrado exitosamente.")
            return redirect('detalle_prestamo', prestamo_id=prestamo.id)
    else:
        form = PrestamoForm(usuario_actual=request.user, initial=initial_data)
    
    return render(request, 'prestamos/crear_prestamo.html', {'form': form})

@login_required
def registrar_devolucion(request, prestamo_id):
    # Solo bibliotecarios pueden registrar devoluciones
    if not request.user.perfil.es_bibliotecario():
        messages.error(request, "No tienes permisos para registrar devoluciones.")
        return redirect('dashboard')
    
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    
    # Verificar si ya fue devuelto
    if prestamo.estado == 'devuelto' or prestamo.estado == 'perdido':
        messages.error(request, "Este préstamo ya fue procesado.")
        return redirect('detalle_prestamo', prestamo_id=prestamo.id)
    
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            devolucion = form.save(commit=False)
            devolucion.prestamo = prestamo
            devolucion.save()
            
            messages.success(request, "Devolución registrada exitosamente.")
            return redirect('detalle_prestamo', prestamo_id=prestamo.id)
    else:
        form = DevolucionForm()
    
    context = {
        'form': form,
        'prestamo': prestamo,
        'dias_retraso': calcular_dias_retraso(prestamo),
    }
    return render(request, 'prestamos/devolucion.html', context)

@login_required
def mis_prestamos(request):
    # Solo docentes pueden ver sus préstamos
    if not request.user.perfil.es_docente():
        messages.error(request, "Esta página es solo para docentes.")
        return redirect('dashboard')
    
    # Filtrar préstamos del usuario actual
    prestamos = Prestamo.objects.filter(usuario=request.user)
    
    # Actualizar estados de préstamos
    for prestamo in prestamos:
        actualizar_estado_prestamo(prestamo)
    
    return render(request, 'prestamos/mis_prestamos.html', {'prestamos': prestamos})

@login_required
def historial_prestamos(request):
    # Para docentes, mostrar solo sus préstamos
    if request.user.perfil.es_docente():
        prestamos = Prestamo.objects.filter(usuario=request.user)
    # Para bibliotecarios y directores, mostrar todos los préstamos
    else:
        prestamos = Prestamo.objects.all()
    
    # Filtrar por usuario si se proporciona
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        prestamos = prestamos.filter(usuario_id=usuario_id)
    
    # Filtrar por estado si se proporciona
    estado = request.GET.get('estado')
    if estado:
        prestamos = prestamos.filter(estado=estado)
    
    # Buscar por título de libro
    query = request.GET.get('q')
    if query:
        prestamos = prestamos.filter(
            Q(libro__titulo__icontains=query) | 
            Q(libro__autor__icontains=query) |
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query)
        )
    
    context = {
        'prestamos': prestamos,
        'estados': Prestamo.ESTADO_CHOICES,
        'estado_seleccionado': estado,
        'query': query,
    }
    
    return render(request, 'prestamos/historial.html', context)

@login_required
def prestamos_retrasados(request):
    # Solo bibliotecarios y directores pueden ver préstamos retrasados
    if not (request.user.perfil.es_bibliotecario() or request.user.perfil.es_director()):
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('dashboard')
    
    # Obtener préstamos retrasados
    prestamos_retrasados = Prestamo.objects.filter(estado='retrasado')
    
    # Filtrar por departamento si se proporciona
    departamento = request.GET.get('departamento')
    if departamento:
        prestamos_retrasados = prestamos_retrasados.filter(usuario__perfil__departamento=departamento)
    
    # Obtener lista de departamentos para el filtro
    departamentos = PerfilUsuario.objects.values_list('departamento', flat=True).distinct()
    
    context = {
        'prestamos': prestamos_retrasados,
        'departamentos': departamentos,
        'departamento_seleccionado': departamento,
    }
    
    return render(request, 'prestamos/prestamos_retrasados.html', context)

@login_required
def detalle_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    
    # Verificar permisos: solo el usuario dueño del préstamo, bibliotecarios o directores
    if (prestamo.usuario != request.user and 
        not request.user.perfil.es_bibliotecario() and 
        not request.user.perfil.es_director()):
        messages.error(request, "No tienes permisos para ver este préstamo.")
        return redirect('dashboard')
    
    # Actualizar estado del préstamo
    actualizar_estado_prestamo(prestamo)
    
    try:
        devolucion = prestamo.devolucion
    except Devolucion.DoesNotExist:
        devolucion = None
    
    context = {
        'prestamo': prestamo,
        'devolucion': devolucion,
        'dias_retraso': calcular_dias_retraso(prestamo),
    }
    
    return render(request, 'prestamos/detalle_prestamo.html', context)
