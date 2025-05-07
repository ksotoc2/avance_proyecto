from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Prestamo, Devolucion
from .forms import PrestamoForm, DevolucionForm
from libros.models import Libro
from usuarios.models import PerfilUsuario
from .services import verificar_stock, actualizar_stock, calcular_dias_retraso, actualizar_estado_prestamo
from reportes.utils import generar_pdf_reporte

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
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(prestamos, 10)  # 10 préstamos por página
    
    try:
        prestamos_paginados = paginator.page(page)
    except PageNotAnInteger:
        prestamos_paginados = paginator.page(1)
    except EmptyPage:
        prestamos_paginados = paginator.page(paginator.num_pages)
    
    # Generar reporte si se solicita
    if request.GET.get('generar_reporte'):
        tipo_reporte = request.GET.get('tipo_reporte', 'todos')
        
        if tipo_reporte == 'activos':
            prestamos_reporte = prestamos.filter(estado__in=['activo', 'retrasado'])
            titulo = "Reporte de Préstamos Activos"
        elif tipo_reporte == 'historial':
            prestamos_reporte = prestamos
            titulo = "Historial Completo de Préstamos"
        else:
            prestamos_reporte = prestamos
            titulo = "Reporte de Préstamos"
        
        # Preparar datos para el reporte
        datos = {
            'columnas': ['Libro', 'Fecha Préstamo', 'Fecha Devolución', 'Estado'],
            'filas': [
                [
                    p.libro.titulo,
                    p.fecha_prestamo.strftime('%d/%m/%Y'),
                    p.fecha_devolucion_esperada.strftime('%d/%m/%Y'),
                    p.get_estado_display()
                ]
                for p in prestamos_reporte
            ]
        }
        
        # Generar el PDF
        return generar_pdf_reporte(
            titulo=titulo,
            datos=datos,
            filtros={
                'Usuario': request.user.get_full_name(),
                'Departamento': request.user.perfil.departamento
            }
        )
    
    return render(request, 'prestamos/mis_prestamos.html', {'prestamos': prestamos_paginados})

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
    
    # Ordenar por fecha de préstamo (más reciente primero)
    prestamos = prestamos.order_by('-fecha_prestamo')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(prestamos, 10)  # 10 préstamos por página
    
    try:
        prestamos_paginados = paginator.page(page)
    except PageNotAnInteger:
        prestamos_paginados = paginator.page(1)
    except EmptyPage:
        prestamos_paginados = paginator.page(paginator.num_pages)
    
    # Generar reporte si se solicita
    if request.GET.get('generar_reporte'):
        tipo_reporte = request.GET.get('tipo_reporte', 'todos')
        
        # Aplicar filtros adicionales según el tipo de reporte
        if tipo_reporte == 'activos':
            prestamos_reporte = prestamos.filter(estado__in=['activo', 'retrasado'])
            titulo = "Reporte de Préstamos Activos"
        elif tipo_reporte == 'retrasados':
            prestamos_reporte = prestamos.filter(estado='retrasado')
            titulo = "Reporte de Préstamos Retrasados"
        else:
            prestamos_reporte = prestamos
            titulo = "Historial Completo de Préstamos"
        
        # Preparar datos para el reporte
        if request.user.perfil.es_docente():
            datos = {
                'columnas': ['Libro', 'Fecha Préstamo', 'Fecha Devolución', 'Estado'],
                'filas': [
                    [
                        p.libro.titulo,
                        p.fecha_prestamo.strftime('%d/%m/%Y'),
                        p.fecha_devolucion_esperada.strftime('%d/%m/%Y'),
                        p.get_estado_display()
                    ]
                    for p in prestamos_reporte
                ]
            }
        else:
            datos = {
                'columnas': ['Libro', 'Usuario', 'Departamento', 'Fecha Préstamo', 'Fecha Devolución', 'Estado'],
                'filas': [
                    [
                        p.libro.titulo,
                        p.usuario.get_full_name(),
                        p.usuario.perfil.departamento,
                        p.fecha_prestamo.strftime('%d/%m/%Y'),
                        p.fecha_devolucion_esperada.strftime('%d/%m/%Y'),
                        p.get_estado_display()
                    ]
                    for p in prestamos_reporte
                ]
            }
        
        # Preparar filtros para el reporte
        filtros = {}
        if usuario_id:
            from django.contrib.auth.models import User
            usuario = User.objects.get(id=usuario_id)
            filtros['Usuario'] = usuario.get_full_name()
        if estado:
            filtros['Estado'] = dict(Prestamo.ESTADO_CHOICES).get(estado)
        if query:
            filtros['Búsqueda'] = query
        
        # Generar el PDF
        return generar_pdf_reporte(titulo=titulo, datos=datos, filtros=filtros)
    
    # Obtener lista de usuarios para el filtro (solo para bibliotecarios y directores)
    usuarios = None
    if request.user.perfil.es_bibliotecario() or request.user.perfil.es_director():
        from django.contrib.auth.models import User
        usuarios = User.objects.filter(perfil__cargo='docente')
    
    context = {
        'prestamos': prestamos_paginados,
        'estados': Prestamo.ESTADO_CHOICES,
        'estado_seleccionado': estado,
        'query': query,
        'usuarios': usuarios,
        'usuario_seleccionado': usuario_id if usuario_id else None,
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
    
    # Ordenar por días de retraso (más retrasados primero)
    prestamos_retrasados = prestamos_retrasados.order_by('-fecha_devolucion_esperada')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(prestamos_retrasados, 10)  # 10 préstamos por página
    
    try:
        prestamos_paginados = paginator.page(page)
    except PageNotAnInteger:
        prestamos_paginados = paginator.page(1)
    except EmptyPage:
        prestamos_paginados = paginator.page(paginator.num_pages)
    
    # Obtener lista de departamentos para el filtro
    departamentos = PerfilUsuario.objects.values_list('departamento', flat=True).distinct()
    
    # Generar reporte si se solicita
    if request.GET.get('generar_reporte'):
        # Preparar datos para el reporte
        datos = {
            'columnas': ['Libro', 'Usuario', 'Departamento', 'Fecha Préstamo', 'Fecha Devolución', 'Días de Retraso'],
            'filas': [
                [
                    p.libro.titulo,
                    p.usuario.get_full_name(),
                    p.usuario.perfil.departamento,
                    p.fecha_prestamo.strftime('%d/%m/%Y'),
                    p.fecha_devolucion_esperada.strftime('%d/%m/%Y'),
                    p.dias_retraso()
                ]
                for p in prestamos_retrasados
            ]
        }
        
        # Preparar filtros para el reporte
        filtros = {}
        if departamento:
            filtros['Departamento'] = departamento
        
        # Generar el PDF
        return generar_pdf_reporte(
            titulo="Reporte de Préstamos Retrasados",
            datos=datos,
            filtros=filtros
        )
    
    context = {
        'prestamos': prestamos_paginados,
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
    
    # Generar reporte si se solicita
    if request.GET.get('generar_reporte'):
        # Preparar datos para el reporte
        datos = {
            'columnas': ['Libro', 'Usuario', 'Departamento', 'Fecha Préstamo', 'Fecha Devolución', 'Estado'],
            'filas': [
                [
                    prestamo.libro.titulo,
                    prestamo.usuario.get_full_name(),
                    prestamo.usuario.perfil.departamento,
                    prestamo.fecha_prestamo.strftime('%d/%m/%Y'),
                    prestamo.fecha_devolucion_esperada.strftime('%d/%m/%Y'),
                    prestamo.get_estado_display()
                ]
            ]
        }
        
        # Añadir información de devolución si existe
        if devolucion:
            datos_devolucion = {
                'columnas': ['Fecha Devolución', 'Estado del Libro', 'Observaciones'],
                'filas': [
                    [
                        devolucion.fecha_devolucion.strftime('%d/%m/%Y'),
                        devolucion.get_estado_libro_display(),
                        devolucion.observacion or "Sin observaciones"
                    ]
                ]
            }
        else:
            datos_devolucion = None
        
        # Generar el PDF
        return generar_pdf_reporte(
            titulo=f"Detalle de Préstamo - {prestamo.libro.titulo}",
            datos=datos,
            filtros={
                'ID Préstamo': prestamo.id,
                'Días de retraso': calcular_dias_retraso(prestamo) if prestamo.estado == 'retrasado' else 0
            }
        )
    
    context = {
        'prestamo': prestamo,
        'devolucion': devolucion,
        'dias_retraso': calcular_dias_retraso(prestamo),
    }
    
    return render(request, 'prestamos/detalle_prestamo.html', context)

@login_required
def libros_inventario(request):
    # Solo bibliotecarios y directores pueden ver el inventario completo
    if not (request.user.perfil.es_bibliotecario() or request.user.perfil.es_director()):
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('dashboard')
    
    # Obtener todos los libros
    libros = Libro.objects.all().select_related('categoria')
    
    # Filtrar por categoría si se proporciona
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        libros = libros.filter(categoria_id=categoria_id)
    
    # Buscar por título o autor
    query = request.GET.get('q')
    if query:
        libros = libros.filter(Q(titulo__icontains=query) | Q(autor__icontains=query))
    
    # Ordenar por título
    libros = libros.order_by('titulo')
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(libros, 10)  # 10 libros por página
    
    try:
        libros_paginados = paginator.page(page)
    except PageNotAnInteger:
        libros_paginados = paginator.page(1)
    except EmptyPage:
        libros_paginados = paginator.page(paginator.num_pages)
    
    # Generar reporte si se solicita
    if request.GET.get('generar_reporte'):
        # Preparar datos para el reporte
        datos = {
            'columnas': ['Título', 'Autor', 'Editorial', 'ISBN', 'Categoría', 'Stock', 'Disponible'],
            'filas': [
                [
                    l.titulo,
                    l.autor,
                    l.editorial,
                    l.isbn,
                    l.categoria.nombre,
                    l.stock,
                    'Sí' if l.disponible() else 'No'
                ]
                for l in libros
            ]
        }
        
        # Preparar filtros para el reporte
        filtros = {}
        if categoria_id:
            from libros.models import CategoriaLibro
            categoria = CategoriaLibro.objects.get(id=categoria_id)
            filtros['Categoría'] = categoria.nombre
        if query:
            filtros['Búsqueda'] = query
        
        # Generar el PDF
        return generar_pdf_reporte(
            titulo="Inventario de Libros",
            datos=datos,
            filtros=filtros
        )
    
    # Obtener categorías para el filtro
    from libros.models import CategoriaLibro
    categorias = CategoriaLibro.objects.all()
    
    context = {
        'libros': libros_paginados,
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'query': query,
    }
    
    return render(request, 'libros/inventario.html', context)
