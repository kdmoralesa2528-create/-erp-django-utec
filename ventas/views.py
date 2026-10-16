from django.shortcuts import render
from .models import Venta, Pedido

def index(request):
    ventas = Venta.objects.all()
    pedidos = Pedido.objects.all()
    
    context = {
        'titulo': 'Ventas',
        'descripcion': 'Registro de ventas e historial',
        'ventas': ventas,
        'pedidos': pedidos,
    }
    return render(request, 'ventas/index.html', context)