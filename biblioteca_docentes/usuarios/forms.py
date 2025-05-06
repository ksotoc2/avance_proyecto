from django import forms
from .models import PerfilUsuario

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['departamento']
        widgets = {
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }
