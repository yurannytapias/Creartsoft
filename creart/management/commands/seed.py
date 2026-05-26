from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from creart.models import Roles, Usuarios

class Command(BaseCommand):
    help = 'Carga datos iniciales: roles y usuarios base'

    def handle(self, *args, **kwargs):
        # Roles
        rol_admin, _ = Roles.objects.get_or_create(
        nombre='administrador',  # ← cambia 'admin' por 'administrador'
        defaults={'descripcion': 'Administrador del sistema'}
)
        rol_vendedor, _ = Roles.objects.get_or_create(
            nombre='vendedor',
            defaults={'descripcion': 'Vendedor de productos'}
        )
        rol_cliente, _ = Roles.objects.get_or_create(
            nombre='cliente',
            defaults={'descripcion': 'Cliente de la tienda'}
        )
        self.stdout.write('✅ Roles creados')

        # Admin
        Usuarios.objects.get_or_create(
            correo='admin@creart.com',
            defaults={
                'nombre': 'Admin',
                'apellido': 'Creart',
                'numero': '0000000000',
                'contrasena': make_password('admin123'),
                'rol': rol_admin,
            }
        )

        # Vendedor
        Usuarios.objects.get_or_create(
            correo='vendedor@creart.com',
            defaults={
                'nombre': 'Vendedor',
                'apellido': 'Demo',
                'numero': '1111111111',
                'contrasena': make_password('vendedor123'),
                'rol': rol_vendedor,
            }
        )

        # Cliente
        Usuarios.objects.get_or_create(
            correo='cliente@creart.com',
            defaults={
                'nombre': 'Cliente',
                'apellido': 'Demo',
                'numero': '2222222222',
                'contrasena': make_password('cliente123'),
                'rol': rol_cliente,
            }
        )

        self.stdout.write('✅ Usuarios creados')
        self.stdout.write(self.style.SUCCESS('🎉 Seed completado'))