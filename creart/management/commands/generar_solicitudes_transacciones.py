import random
from datetime import timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from creart.models import Usuarios, Productos, Solicitudes, Transacciones

NOMBRES_PRODUCTOS_NUEVOS = [
    # Antojos
    'Cupcake Red Velvet', 'Brownie con Nueces', 'Dona Glaseada de Chocolate',
    'Muffin de Arándanos', 'Macarons Surtidos',
    # Diarios
    'Torta de Vainilla Clásica', 'Torta de Zanahoria', 'Torta Red Velvet',
    'Torta de Chocolate Húmeda', 'Torta Tres Leches',
    # Eventos
    'Pastel de Boda 3 Pisos', 'Pastel de Grado 2 Pisos', 'Pastel Quinceañera Floral',
    'Pastel Baby Shower Encanto', 'Pastel Naked Cake Floral',
]


class Command(BaseCommand):
    help = 'Genera 15 solicitudes y 15 transacciones usando los productos ya registrados manualmente'

    def handle(self, *args, **kwargs):
        productos = list(Productos.objects.filter(nombre__in=NOMBRES_PRODUCTOS_NUEVOS))

        if not productos:
            self.stdout.write(self.style.ERROR(
                '❌ No se encontraron productos con esos nombres. Verifica que los hayas registrado igual a como te los pasé.'
            ))
            return

        self.stdout.write(f'📦 {len(productos)} productos encontrados')

        clientes = list(Usuarios.objects.filter(rol__nombre__iexact='cliente'))
        if not clientes:
            self.stdout.write(self.style.ERROR('❌ No hay clientes registrados en la base de datos.'))
            return

        self.stdout.write(f'👥 {len(clientes)} clientes encontrados')

        # Evita duplicar si ya corrió antes para estos productos
        if Solicitudes.objects.filter(producto__in=productos).exists():
            self.stdout.write(self.style.WARNING(
                '⚠️ Ya existen solicitudes para estos productos. Comando omitido para evitar duplicados.'
            ))
            return

        # ══════════════════════════════════════════════
        # SOLICITUDES — 15, distribuidas:
        # 5 pagada, 5 aceptada, 3 pendiente, 2 rechazada
        # ══════════════════════════════════════════════
        estados_solicitudes = (
            ['pagada'] * 5 + ['aceptada'] * 5 + ['pendiente'] * 3 + ['rechazada'] * 2
        )
        random.shuffle(estados_solicitudes)

        coberturas = ['Chocolate', 'Fondant blanco', 'Crema chantilly', 'Ganache', 'Merengue']
        rellenos_opciones = ['Arequipe', 'Frutos rojos', 'Crema pastelera', 'Nutella', 'Maracuyá']
        decoraciones = ['Flores de azúcar', 'Perlas comestibles', 'Topper personalizado', 'Frutas frescas', 'Chocolate rallado']

        solicitudes_creadas = []
        for i in range(15):
            cliente = random.choice(clientes)
            producto = productos[i % len(productos)]
            estado = estados_solicitudes[i]
            precio_total = producto.precio + Decimal(random.randint(0, 20000))
            abono = precio_total * Decimal('0.5') if estado in ['pagada', 'aceptada'] else Decimal(0)

            s = Solicitudes.objects.create(
                usuario=cliente,
                producto=producto,
                nombre_invitado=f'{cliente.nombre} {cliente.apellido}',
                direccion_entrega=cliente.direccion or 'Recoger en tienda',
                tipo_entrega=random.choice(['domicilio', 'tienda']),
                descripcion=f'Solicitud personalizada de {producto.nombre}',
                mensaje_pastel=random.choice(['¡Feliz Cumpleaños!', 'Con amor', 'Felicidades', '']),
                cobertura=random.choice(coberturas),
                rellenos=random.choice(rellenos_opciones),
                decoracion=random.choice(decoraciones),
                pisos=random.randint(1, 3) if producto.categoria == 'eventos' else 1,
                porciones=random.randint(10, 80),
                fecha_evento=date.today() + timedelta(days=random.randint(3, 60)),
                precio_total=precio_total,
                abono=abono,
                estado=estado,
            )
            solicitudes_creadas.append(s)

        self.stdout.write('✅ 15 solicitudes creadas (5 pagadas, 5 aceptadas, 3 pendientes, 2 rechazadas)')

        # ══════════════════════════════════════════════
        # TRANSACCIONES — 15, ligadas a solicitudes pagadas/aceptadas cuando sea posible
        # ══════════════════════════════════════════════
        metodos_pago = ['Tarjeta de crédito', 'PSE', 'Efectivo', 'Transferencia', 'MercadoPago']
        solicitudes_con_pago = [s for s in solicitudes_creadas if s.estado in ['pagada', 'aceptada']]

        for i in range(15):
            solicitud = solicitudes_con_pago[i % len(solicitudes_con_pago)] if solicitudes_con_pago else random.choice(solicitudes_creadas)
            importe = solicitud.precio_total if solicitud.precio_total > 0 else Decimal(random.randint(20000, 200000))
            estado_abono = 'terminado' if solicitud.estado == 'pagada' else 'abonado'

            Transacciones.objects.create(
                hora=time(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                importe_total=importe,
                moneda='COP',
                comisiones=round(importe * Decimal('0.035'), 2),
                metodo_pago=random.choice(metodos_pago),
                token=f'tok_{random.randint(100000, 999999)}****',
                ip_cliente=f'190.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}',
                solicitud=solicitud,
                estado=estado_abono,
            )

        self.stdout.write('✅ 15 transacciones creadas')
        self.stdout.write(self.style.SUCCESS('🎉 Solicitudes y transacciones generadas exitosamente'))