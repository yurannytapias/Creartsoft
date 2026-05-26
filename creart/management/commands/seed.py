from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from creart.models import Roles, Usuarios

class Command(BaseCommand):
    help = 'Carga datos iniciales: roles y usuarios base'

    def handle(self, *args, **kwargs):
        # Limpia datos viejos
        Usuarios.objects.all().delete()
        Roles.objects.all().delete()
        self.stdout.write('🗑️ Datos viejos eliminados')

        # Roles
        rol_admin = Roles.objects.create(
            nombre='administrador',
            descripcion='Administrador del sistema'
        )
        rol_vendedor = Roles.objects.create(
            nombre='vendedor',
            descripcion='Vendedor de productos'
        )
        rol_cliente = Roles.objects.create(
            nombre='cliente',
            descripcion='Cliente de la tienda'
        )
        self.stdout.write('✅ Roles creados')

        # Usuarios
        Usuarios.objects.create(
            correo='admin@creart.com',
            nombre='Admin',
            apellido='Creart',
            numero='0000000000',
            contrasena=make_password('admin123'),
            rol=rol_admin,
        )
        Usuarios.objects.create(
            correo='vendedor@creart.com',
            nombre='Vendedor',
            apellido='Demo',
            numero='1111111111',
            contrasena=make_password('vendedor123'),
            rol=rol_vendedor,
        )
        Usuarios.objects.create(
            correo='cliente@creart.com',
            nombre='Cliente',
            apellido='Demo',
            numero='2222222222',
            contrasena=make_password('cliente123'),
            rol=rol_cliente,
        )
        self.stdout.write('✅ Usuarios creados')
        self.stdout.write(self.style.SUCCESS('🎉 Seed completado'))