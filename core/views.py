from django.shortcuts import render

def bienvenida(request):
    modulos = [
        {'nombre': 'Clientes', 'icono': '👥', 'descripcion': 'Gestión de cartera de clientes', 'url': '/clientes/'},
        {'nombre': 'Productos', 'icono': '📦', 'descripcion': 'Catálogo e inventario', 'url': '/productos/'},
        {'nombre': 'Proveedores', 'icono': '🏭', 'descripcion': 'Compras y proveedores', 'url': '/proveedores/'},
        {'nombre': 'Ventas', 'icono': '🛒', 'descripcion': 'Registro de ventas', 'url': '/ventas/'},
        {'nombre': 'Reportes', 'icono': '📊', 'descripcion': 'Indicadores y métricas', 'url': '/reportes/'},
        {'nombre': 'Admin', 'icono': '⚙️', 'descripcion': 'Gestión y administración del sistema', 'url': '/admin/'},
    ]
    return render(request, 'bienvenida.html', {'modulos': modulos})