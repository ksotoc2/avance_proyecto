from django import forms
from django.contrib.auth.models import User
from .models import Prestamo, Devolucion
from libros.models import Libro
from django.utils import timezone
from datetime import timedelta

class PrestamoForm(forms.ModelForm):
    fecha_devolucion_esperada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date() + timedelta(days=15)
    )
    
    class Meta:
        model = Prestamo
        fields = ['usuario', 'libro', 'fecha_devolucion_esperada']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'libro': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.usuario_actual = kwargs.pop('usuario_actual', None)
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios docentes
        self.fields['usuario'].queryset = User.objects.filter(perfil__cargo='docente')
        # Filtrar solo libros con stock disponible
        self.fields['libro'].queryset = Libro.objects.filter(stock__gt=0)
        
        # Si se proporciona un libro preseleccionado en la URL
        libro_id = None
        if 'initial' in kwargs and 'libro' in kwargs['initial']:
            libro_id = kwargs['initial']['libro']
        elif args and 'libro' in args[0]:
            libro_id = args[0]['libro']
        
        if libro_id:
            try:
                # Excluir docentes que ya tienen este libro prestado
                from prestamos.models import Prestamo
                prestamos_activos = Prestamo.objects.filter(
                    libro_id=libro_id,
                    estado__in=['activo', 'retrasado']
                ).values_list('usuario_id', flat=True)
                
                self.fields['usuario'].queryset = self.fields['usuario'].queryset.exclude(
                    id__in=prestamos_activos
                )
            except Exception:
                pass

class DevolucionForm(forms.ModelForm):
    fecha_devolucion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    
    class Meta:
        model = Devolucion
        fields = ['fecha_devolucion', 'estado_libro', 'observacion']
        widgets = {
            'estado_libro': forms.Select(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
