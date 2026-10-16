from django.shortcuts import render
from .models import Cliente

def index(request):
    clientes = Cliente.objects.all()
    
    context = {
        'titulo': 'Clientes',
        'descripcion': 'Gestión de cartera de clientes',
        'clientes': clientes,
    }
    return render(request, 'clientes/index.html', context)