from django.shortcuts import render
from .models import Proveedor

def index(request):
    # Consultamos los proveedores guardados en la Base de Datos
    proveedores = Proveedor.objects.all()
    
    context = {
        'titulo': 'Proveedores',
        'descripcion': 'Gestión de proveedores de mercancía',
        'proveedores': proveedores,
    }
    return render(request, 'proveedores/index.html', context)