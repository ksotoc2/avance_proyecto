from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nuevo/', views.registrar_prestamo, name='registrar_prestamo'),
    path('devolucion/<int:prestamo_id>/', views.registrar_devolucion, name='registrar_devolucion'),
    path('mis-prestamos/', views.mis_prestamos, name='mis_prestamos'),
    path('historial/', views.historial_prestamos, name='historial_prestamos'),
    path('retrasados/', views.prestamos_retrasados, name='prestamos_retrasados'),
    path('<int:prestamo_id>/', views.detalle_prestamo, name='detalle_prestamo'),
]
