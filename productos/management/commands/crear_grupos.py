from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Crea los grupos por defecto (Gerente, Vendedor, Almacén) y asigna permisos.'

    def handle(self, *args, **kwargs):
        # Grupo Gerente
        gerente, _ = Group.objects.get_or_create(name='Gerente')
        perms_gerente = Permission.objects.filter(
            codename__in=['delete_producto', 'delete_cliente', 'delete_venta', 'add_venta']
        )
        gerente.permissions.set(perms_gerente)

        # Grupo Vendedor
        vendedor, _ = Group.objects.get_or_create(name='Vendedor')
        perms_vendedor = Permission.objects.filter(
            codename__in=['add_venta', 'view_producto', 'view_cliente']
        )
        vendedor.permissions.set(perms_vendedor)

        # Grupo Almacén
        almacen, _ = Group.objects.get_or_create(name='Almacén')
        perms_almacen = Permission.objects.filter(
            codename__in=['add_producto', 'change_producto', 'view_producto']
        )
        almacen.permissions.set(perms_almacen)

        self.stdout.write(self.style.SUCCESS('¡Grupos y permisos creados exitosamente!'))