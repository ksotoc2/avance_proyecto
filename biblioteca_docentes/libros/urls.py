from django.urls import path
from . import views
from prestamos.views import libros_inventario

urlpatterns = [
    path('', views.lista_libros, name='lista_libros'),
    path('<int:libro_id>/', views.detalle_libro, name='detalle_libro'),
    path('nuevo/', views.editar_libro, name='nuevo_libro'),
    path('editar/<int:libro_id>/', views.editar_libro, name='editar_libro'),
    path('eliminar/<int:libro_id>/', views.eliminar_libro, name='eliminar_libro'),
    path('inventario/', libros_inventario, name='libros_inventario'),
]
