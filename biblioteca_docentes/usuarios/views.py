from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib import messages
from .models import PerfilUsuario
from .forms import PerfilUsuarioForm

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')

@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user.perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user.perfil)
    
    return render(request, 'usuarios/perfil.html', {'form': form})

class RegistroUsuarioView(CreateView):
    form_class = UserCreationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('login')
