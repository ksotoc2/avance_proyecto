from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Libro, CategoriaLibro
from .forms import LibroForm

@login_required
def lista_libros(request):
    libros = Libro.objects.all()
    categorias = CategoriaLibro.objects.all()
    
    # Filtrar por categoría si se proporciona
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        libros = libros.filter(categoria_id=categoria_id)
    
    # Buscar por título o autor
    query = request.GET.get('q')
    if query:
        libros = libros.filter(titulo__icontains=query) | libros.filter(autor__icontains=query)
    
    context = {
        'libros': libros,
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'query': query,
    }
    
    return render(request, 'libros/lista_libros.html', context)

@login_required
def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    
    # Obtener préstamos activos de este libro
    from prestamos.models import Prestamo
    prestamos_activos = Prestamo.objects.filter(
        libro=libro,
        estado__in=['activo', 'retrasado']
    ).select_related('usuario', 'usuario__perfil')
    
    context = {
        'libro': libro,
        'prestamos_activos': prestamos_activos,
        'puede_prestar': True
    }
    
    # Verificar si el usuario actual (si es docente) ya tiene este libro prestado
    if request.user.perfil.es_docente():
        prestamo_usuario = prestamos_activos.filter(usuario=request.user).exists()
        if prestamo_usuario:
            context['puede_prestar'] = False
            context['mensaje_prestamo'] = "Ya tienes este libro prestado actualmente."
    
    return render(request, 'libros/detalle_libro.html', context)

@login_required
def editar_libro(request, libro_id=None):
    # Verificar si el usuario es bibliotecario
    if not request.user.perfil.es_bibliotecario():
        messages.error(request, "No tienes permisos para editar libros.")
        return redirect('lista_libros')
    
    # Obtener el libro o crear uno nuevo
    if libro_id:
        libro = get_object_or_404(Libro, id=libro_id)
        titulo_pagina = f"Editar Libro: {libro.titulo}"
    else:
        libro = None
        titulo_pagina = "Nuevo Libro"
    
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, "Libro guardado exitosamente.")
            return redirect('lista_libros')
    else:
        form = LibroForm(instance=libro)
    
    return render(request, 'libros/editar_libro.html', {
        'form': form,
        'libro': libro,
        'titulo_pagina': titulo_pagina
    })

@login_required
def eliminar_libro(request, libro_id):
    # Verificar si el usuario es bibliotecario
    if not request.user.perfil.es_bibliotecario():
        messages.error(request, "No tienes permisos para eliminar libros.")
        return redirect('lista_libros')
    
    libro = get_object_or_404(Libro, id=libro_id)
    
    if request.method == 'POST':
        libro.delete()
        messages.success(request, f"El libro '{libro.titulo}' ha sido eliminado.")
        return redirect('lista_libros')
    
    return render(request, 'libros/confirmar_eliminar.html', {'libro': libro})
