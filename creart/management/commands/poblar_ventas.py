import random
from datetime import timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from creart.models import (
    Roles, Usuarios, Productos, Solicitudes, Transacciones,
    PQRS, Proveedores, Inventario, Movimiento
)


class Command(BaseCommand):
    help = (
        'Crea 15 usuarios clientes, 15 solicitudes, 15 transacciones, 15 PQRS '
        'usando los productos reales ya creados por el vendedor, '
        'y agrega registros adicionales a Inventario. No borra nada existente.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--vendedor',
            type=str,
            default='vendedor@creart.com',
            help='Correo del vendedor real al que pertenecen los productos.',
        )

    def handle(self, *args, **kwargs):
        correo_vendedor = kwargs['vendedor']

        try:
            vendedor = Usuarios.objects.get(correo=correo_vendedor)
        except Usuarios.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'No existe un usuario con correo {correo_vendedor}. Aborto.'
            ))
            return

        productos_vendedor = list(Productos.objects.filter(vendedor=vendedor))
        if not productos_vendedor:
            self.stdout.write(self.style.ERROR(
                f'El vendedor {correo_vendedor} no tiene productos registrados. '
                'Crea los productos primero.'
            ))
            return

        self.stdout.write(self.style.NOTICE(
            f'Usando {len(productos_vendedor)} productos de {correo_vendedor}'
        ))

        rol_cliente, _ = Roles.objects.get_or_create(
            nombre='cliente', defaults={'descripcion': 'Cliente de la tienda'}
        )

        nombres = ['Laura', 'Carlos', 'Mariana', 'Andres', 'Valentina', 'Felipe', 'Camila',
                   'Santiago', 'Isabella', 'Daniel', 'Sara', 'Juan', 'Paula', 'David', 'Natalia']
        apellidos = ['Gomez', 'Rodriguez', 'Perez', 'Martinez', 'Lopez', 'Garcia', 'Hernandez',
                     'Diaz', 'Torres', 'Ramirez', 'Florez', 'Castro', 'Suarez', 'Ortiz', 'Vargas']

        clientes = []
        for i in range(15):
            correo = f'cliente{i+1}@creart.com'
            if Usuarios.objects.filter(correo=correo).exists():
                u = Usuarios.objects.get(correo=correo)
            else:
                u = Usuarios.objects.create(
                    correo=correo,
                    nombre=nombres[i],
                    apellido=apellidos[i],
                    numero=f'30{random.randint(10000000, 99999999)}',
                    contrasena=make_password('cliente1234'),
                    rol=rol_cliente,
                    direccion=f'Calle {random.randint(1,150)} #{random.randint(1,99)}-{random.randint(1,99)}, Bogota',
                )
            clientes.append(u)

        self.stdout.write(self.style.SUCCESS(
            f'{len(clientes)} clientes listos (cliente1@creart.com ... cliente15@creart.com, clave: cliente1234)'
        ))

        estados_solicitudes = (
            ['pagada'] * 5 + ['aceptada'] * 5 + ['pendiente'] * 3 + ['rechazada'] * 2
        )
        random.shuffle(estados_solicitudes)

        coberturas = ['Chocolate', 'Fondant blanco', 'Crema chantilly', 'Ganache', 'Merengue']
        rellenos_opciones = ['Arequipe', 'Frutos rojos', 'Crema pastelera', 'Nutella', 'Maracuya']
        decoraciones = ['Flores de azucar', 'Perlas comestibles', 'Topper personalizado', 'Frutas frescas', 'Chocolate rallado']

        solicitudes_creadas = []
        for i in range(15):
            cliente = random.choice(clientes)
            producto = random.choice(productos_vendedor)
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
                mensaje_pastel=random.choice(['Feliz Cumpleanos!', 'Con amor', 'Felicidades', '']),
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

        self.stdout.write(self.style.SUCCESS(
            '15 solicitudes creadas (5 pagadas, 5 aceptadas, 3 pendientes, 2 rechazadas)'
        ))

        metodos_pago = ['Tarjeta de credito', 'PSE', 'Efectivo', 'Transferencia', 'MercadoPago']
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

        self.stdout.write(self.style.SUCCESS('15 transacciones creadas'))

        asuntos_categorias = [
            ('pregunta', 'Cual es el tiempo de entrega?', 'Cuanto tiempo tarda en estar listo un pedido personalizado?'),
            ('pregunta', 'Disponibilidad de sabores', 'Tienen disponible el sabor de maracuya para pedidos grandes?'),
            ('queja', 'Retraso en la entrega', 'Mi pedido llego dos horas tarde al evento.'),
            ('queja', 'Producto no coincidia con la foto', 'El pastel no se veia igual a la imagen del catalogo.'),
            ('reporte', 'Error en el cobro', 'Se me cobro dos veces por la misma solicitud.'),
            ('reporte', 'Problema con la pagina', 'No pude completar el pago desde el movil.'),
            ('solicitud', 'Cambio de fecha de entrega', 'Necesito mover la fecha de mi pedido para la proxima semana.'),
            ('solicitud', 'Solicitud de factura', 'Quisiera la factura electronica de mi compra.'),
            ('pregunta', 'Metodos de pago', 'Aceptan pagos en cuotas?'),
            ('queja', 'Atencion al cliente', 'Tardaron mucho en responder mi mensaje anterior.'),
            ('reporte', 'Producto danado', 'El pastel llego con la decoracion danada.'),
            ('solicitud', 'Pedido personalizado especial', 'Quiero un diseno totalmente personalizado para un evento.'),
            ('pregunta', 'Ingredientes y alergias', 'Tienen opciones sin gluten o sin lacteos?'),
            ('queja', 'Tamano del pedido', 'El pastel era mas pequeno de lo que esperaba.'),
            ('solicitud', 'Reembolso', 'Quisiera solicitar el reembolso de mi pedido cancelado.'),
        ]

        for i, (categoria, asunto, mensaje) in enumerate(asuntos_categorias):
            cliente = clientes[i % len(clientes)]
            tiene_respuesta = i % 2 == 0
            PQRS.objects.create(
                asunto=asunto,
                mensaje=mensaje,
                usuario=cliente,
                respuesta='Gracias por tu mensaje, ya hemos tomado nota y resolveremos esto a la brevedad.' if tiene_respuesta else None,
                estado_respuesta='respondido' if tiene_respuesta else 'sin_respuesta',
                categoria=categoria,
            )

        self.stdout.write(self.style.SUCCESS('15 PQRS creadas'))

        proveedores_data = [
            ('Harinas del Valle', 'Distribuidora de harinas y endulzantes'),
            ('Lacteos La Sabana', 'Proveedor de lacteos y derivados'),
            ('Chocolates Finos SAS', 'Importador de chocolates y cacao'),
            ('Frutas Frescas del Campo', 'Distribuidora de frutas'),
            ('Insumos Reposteros Bogota', 'Insumos generales de reposteria'),
        ]
        proveedores_creados = list(Proveedores.objects.all())
        if not proveedores_creados:
            for nombre_emp, desc in proveedores_data:
                prov = Proveedores.objects.create(
                    nombre=nombre_emp.split()[0],
                    apellido='Proveedor',
                    numero=f'31{random.randint(10000000, 99999999)}',
                    correo=f'contacto@{nombre_emp.lower().replace(" ", "")[:15]}.com',
                    direccion=f'Zona Industrial #{random.randint(1,50)}, Bogota',
                    empresa=nombre_emp,
                )
                proveedores_creados.append(prov)
            self.stdout.write(self.style.SUCCESS('5 proveedores creados'))
        else:
            self.stdout.write(self.style.NOTICE(
                f'Ya existian {len(proveedores_creados)} proveedores, no se crearon nuevos.'
            ))

        inventario_data = [
            ('Harina de trigo', 'harinas', 'kg', 50, 10, 3500),
            ('Harina de almendra', 'harinas', 'kg', 20, 5, 18000),
            ('Leche entera', 'lacteos', 'l', 40, 8, 3200),
            ('Crema de leche', 'lacteos', 'l', 25, 5, 9500),
            ('Mantequilla', 'lacteos', 'kg', 30, 6, 14000),
            ('Azucar blanca', 'endulzantes', 'kg', 60, 15, 2800),
            ('Azucar pulverizada', 'endulzantes', 'kg', 25, 5, 4200),
            ('Ron anejo', 'licores', 'ml', 3000, 500, 45000),
            ('Fresas', 'frutas', 'kg', 15, 3, 8000),
            ('Maracuya', 'frutas', 'kg', 10, 2, 6500),
            ('Chocolate negro 70%', 'chocolates', 'kg', 20, 4, 28000),
            ('Chocolate blanco', 'chocolates', 'kg', 15, 3, 26000),
            ('Aceite vegetal', 'aceites', 'l', 20, 5, 7500),
            ('Huevos', 'huevos', 'g', 600, 100, 450),
            ('Frutos rojos mixtos', 'frutos_rojos', 'kg', 12, 3, 15000),
        ]

        creados_inventario = 0
        for nombre_ing, categoria, unidad, cantidad, stock_min, precio in inventario_data:
            if Inventario.objects.filter(nombre=nombre_ing).exists():
                continue
            inv = Inventario.objects.create(
                id_proveedor=random.choice(proveedores_creados),
                nombre=nombre_ing,
                descripcion=f'{nombre_ing} de alta calidad para reposteria',
                cantidad=cantidad,
                precio_unitario=Decimal(precio),
                stock_minimo=stock_min,
                unidad=unidad,
                categoria=categoria,
            )
            Movimiento.objects.create(
                id_inventario=inv,
                cantidad=cantidad,
                tipo='entrada',
                costo_unitario=Decimal(precio),
                observacion='Carga inicial de inventario',
            )
            creados_inventario += 1

        self.stdout.write(self.style.SUCCESS(
            f'{creados_inventario} registros nuevos de inventario creados (los existentes no se duplicaron)'
        ))

        self.stdout.write(self.style.SUCCESS('Poblado completo finalizado exitosamente'))
