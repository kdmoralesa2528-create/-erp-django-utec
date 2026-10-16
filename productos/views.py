from django.shortcuts import render
from .models import Producto, Categoria

def index(request):
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.all()
    
    context = {
        'titulo': 'Productos',
        'descripcion': 'Catálogo e inventario',
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'productos/index.html', context)