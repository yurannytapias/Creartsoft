from django.core.management.base import BaseCommand
from creart.models import Productos, Solicitudes, Transacciones

NOMBRES_PRODUCTOS_PRUEBA = [
    'Pastel Baby Shower Encanto', 'Pastel de Boda 3 Pisos',
    'Pastel de Grado 2 Pisos', 'Pastel Naked Floral',
    'Pastel Quinceañera 2 Pisos',
    'Torta de Chocolate Clásica', 'Torta Red Velvet',
    'Torta de Zanahoria', 'Torta Vainilla con Fresas',
    'Torta Mousse de Maracuyá',
    'Cupcake Decorado', 'Brownie con Nueces',
    'Dona Glaseada', 'Muffin de Arándanos',
    'Macarons Surtidos',
]


class Command(BaseCommand):
    help = 'Borra los 15 productos de prueba de poblar_datos junto con sus solicitudes y transacciones'

    def handle(self, *args, **kwargs):
        productos = Productos.objects.filter(nombre__in=NOMBRES_PRODUCTOS_PRUEBA)
        total_productos = productos.count()

        if total_productos == 0:
            self.stdout.write(self.style.WARNING('⚠️ No se encontraron productos de prueba para borrar.'))
            return

        solicitudes = Solicitudes.objects.filter(producto__in=productos)
        transacciones = Transacciones.objects.filter(solicitud__in=solicitudes)

        total_transacciones = transacciones.count()
        total_solicitudes = solicitudes.count()

        transacciones.delete()
        self.stdout.write(f'🗑️ {total_transacciones} transacciones eliminadas')

        solicitudes.delete()
        self.stdout.write(f'🗑️ {total_solicitudes} solicitudes eliminadas')

        productos.delete()
        self.stdout.write(f'🗑️ {total_productos} productos eliminados')

        self.stdout.write(self.style.SUCCESS('🎉 Limpieza de datos de prueba completada'))