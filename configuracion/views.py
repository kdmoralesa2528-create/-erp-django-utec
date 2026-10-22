from django.shortcuts import render
from .models import ConfiguracionERP

def index(request):
    config = ConfiguracionERP.get_instance()
    
    context = {
        'titulo': 'Configuración ERP',
        'config': config,
    }
    return render(request, 'configuracion/index.html', context)