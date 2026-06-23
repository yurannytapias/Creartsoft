import random
from datetime import timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from creart.models import (
    Roles, Usuarios, Productos, Solicitudes, Transacciones,
    PQRS, Proveedores, Inventario, Movimiento
)


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba (productos, usuarios, transacciones, pqrs, solicitudes, inventario)'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Iniciando poblado de datos...')

        # ══════════════════════════════════════════════
        # ROLES (usa los existentes o los crea si no están)
        # ══════════════════════════════════════════════
        rol_admin, _ = Roles.objects.get_or_create(
            nombre='administrador', defaults={'descripcion': 'Administrador del sistema'}
        )
        rol_vendedor, _ = Roles.objects.get_or_create(
            nombre='vendedor', defaults={'descripcion': 'Vendedor de productos'}
        )
        rol_cliente, _ = Roles.objects.get_or_create(
            nombre='cliente', defaults={'descripcion': 'Cliente de la tienda'}
        )

        # ══════════════════════════════════════════════
        # USUARIOS — 15 nuevos (sin contar admin@creart.com y vendedor@creart.com)
        # 1 admin extra, 1 vendedor extra, 13 clientes
        # ══════════════════════════════════════════════
        nombres = ['Laura', 'Carlos', 'Mariana', 'Andrés', 'Valentina', 'Felipe', 'Camila',
                   'Santiago', 'Isabella', 'Daniel', 'Sara', 'Juan', 'Paula', 'David', 'Natalia']
        apellidos = ['Gómez', 'Rodríguez', 'Pérez', 'Martínez', 'López', 'García', 'Hernández',
                     'Díaz', 'Torres', 'Ramírez', 'Flórez', 'Castro', 'Suárez', 'Ortiz', 'Vargas']

        usuarios_creados = []

        # 1 admin extra
        u = Usuarios.objects.create(
            correo='admin2@creart.com',
            nombre=nombres[0],
            apellido=apellidos[0],
            numero=f'30{random.randint(10000000, 99999999)}',
            contrasena=make_password('admin1234'),
            rol=rol_admin,
        )
        usuarios_creados.append(u)
        self.stdout.write('✅ Administrador extra creado (admin2@creart.com)')

        # 1 vendedor extra
        u = Usuarios.objects.create(
            correo='vendedor2@creart.com',
            nombre=nombres[1],
            apellido=apellidos[1],
            numero=f'30{random.randint(10000000, 99999999)}',
            contrasena=make_password('vendedor1234'),
            rol=rol_vendedor,
        )
        usuarios_creados.append(u)
        self.stdout.write('✅ Vendedor extra creado (vendedor2@creart.com)')

        # 13 clientes
        clientes = []
        for i in range(13):
            correo = f'cliente{i+1}@creart.com'
            u = Usuarios.objects.create(
                correo=correo,
                nombre=nombres[i + 2],
                apellido=apellidos[i + 2],
                numero=f'30{random.randint(10000000, 99999999)}',
                contrasena=make_password('cliente1234'),
                rol=rol_cliente,
                direccion=f'Calle {random.randint(1,150)} #{random.randint(1,99)}-{random.randint(1,99)}, Bogotá',
            )
            clientes.append(u)
            usuarios_creados.append(u)
        self.stdout.write(f'✅ {len(clientes)} clientes creados (cliente1@creart.com ... cliente13@creart.com)')

        # Vendedor existente para asignar productos
        try:
            vendedor_principal = Usuarios.objects.get(correo='vendedor@creart.com')
        except Usuarios.DoesNotExist:
            vendedor_principal = usuarios_creados[1]  # vendedor2 como respaldo

        # ══════════════════════════════════════════════
        # PRODUCTOS — 15 (5 eventos / 5 diarios / 5 antojos)
        # Reutiliza imágenes ya existentes en media/productos/
        # ══════════════════════════════════════════════
        imagenes_eventos = [
            'productos/pastel_baby_shower.jpg', 'productos/pastel_bodas_3pisos.jpg',
            'productos/pastel_grados_2pisos.jpg', 'productos/pastel_naked_floral.jpg',
            'productos/pastel_quinceanera_2pisos.jpg',
        ]
        imagenes_diarios = [
            'productos/torta_chocolate.jpg', 'productos/torta_red_velvet.jpg',
            'productos/torta_zanahoria.jpg', 'productos/torta_vainilla_fresas.jpg',
            'productos/torta_mousse_maracuya.jpg',
        ]
        imagenes_antojos = [
            'productos/cupcake.jpg', 'productos/brownie.jpg',
            'productos/dona.jpg', 'productos/muffin_arandanos.jpg',
            'productos/macarons_surtidos.jpg',
        ]

        nombres_eventos = ['Pastel Baby Shower Encanto', 'Pastel de Boda 3 Pisos',
                           'Pastel de Grado 2 Pisos', 'Pastel Naked Floral',
                           'Pastel Quinceañera 2 Pisos']
        nombres_diarios = ['Torta de Chocolate Clásica', 'Torta Red Velvet',
                           'Torta de Zanahoria', 'Torta Vainilla con Fresas',
                           'Torta Mousse de Maracuyá']
        nombres_antojos = ['Cupcake Decorado', 'Brownie con Nueces',
                           'Dona Glaseada', 'Muffin de Arándanos',
                           'Macarons Surtidos']

        productos_creados = {'eventos': [], 'diarios': [], 'antojos': []}

        for categoria, nombres_p, imagenes in [
            ('eventos', nombres_eventos, imagenes_eventos),
            ('diarios', nombres_diarios, imagenes_diarios),
            ('antojos', nombres_antojos, imagenes_antojos),
        ]:
            for nombre_p, imagen in zip(nombres_p, imagenes):
                precio_base = {
                    'eventos': random.randint(180000, 450000),
                    'diarios': random.randint(45000, 90000),
                    'antojos': random.randint(5000, 15000),
                }[categoria]

                p = Productos.objects.create(
                    nombre=nombre_p,
                    descripcion=f'Delicioso producto de pastelería: {nombre_p}. Elaborado con ingredientes frescos y de la mejor calidad.',
                    precio=Decimal(precio_base),
                    imagen=imagen,
                    vendedor=vendedor_principal,
                    categoria=categoria,
                    estado_aprobacion='aprobado',
                )
                productos_creados[categoria].append(p)

        self.stdout.write('✅ 15 productos creados (5 eventos, 5 diarios, 5 antojos)')

        todos_productos = productos_creados['eventos'] + productos_creados['diarios'] + productos_creados['antojos']

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
            producto = random.choice(todos_productos)
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

        # ══════════════════════════════════════════════
        # PQRS — 15, de los clientes registrados
        # ══════════════════════════════════════════════
        asuntos_categorias = [
            ('pregunta', '¿Cuál es el tiempo de entrega?', '¿Cuánto tiempo tarda en estar listo un pedido personalizado?'),
            ('pregunta', 'Disponibilidad de sabores', '¿Tienen disponible el sabor de maracuyá para pedidos grandes?'),
            ('queja', 'Retraso en la entrega', 'Mi pedido llegó dos horas tarde al evento.'),
            ('queja', 'Producto no coincidía con la foto', 'El pastel no se veía igual a la imagen del catálogo.'),
            ('reporte', 'Error en el cobro', 'Se me cobró dos veces por la misma solicitud.'),
            ('reporte', 'Problema con la página', 'No pude completar el pago desde el móvil.'),
            ('solicitud', 'Cambio de fecha de entrega', 'Necesito mover la fecha de mi pedido para la próxima semana.'),
            ('solicitud', 'Solicitud de factura', 'Quisiera la factura electrónica de mi compra.'),
            ('pregunta', 'Métodos de pago', '¿Aceptan pagos en cuotas?'),
            ('queja', 'Atención al cliente', 'Tardaron mucho en responder mi mensaje anterior.'),
            ('reporte', 'Producto dañado', 'El pastel llegó con la decoración dañada.'),
            ('solicitud', 'Pedido personalizado especial', 'Quiero un diseño totalmente personalizado para un evento.'),
            ('pregunta', 'Ingredientes y alergias', '¿Tienen opciones sin gluten o sin lácteos?'),
            ('queja', 'Tamaño del pedido', 'El pastel era más pequeño de lo que esperaba.'),
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

        self.stdout.write('✅ 15 PQRS creadas (de los clientes registrados)')

        # ══════════════════════════════════════════════
        # PROVEEDORES — necesarios para el inventario
        # ══════════════════════════════════════════════
        proveedores_data = [
            ('Harinas del Valle', 'Distribuidora de harinas y endulzantes'),
            ('Lácteos La Sabana', 'Proveedor de lácteos y derivados'),
            ('Chocolates Finos SAS', 'Importador de chocolates y cacao'),
            ('Frutas Frescas del Campo', 'Distribuidora de frutas'),
            ('Insumos Reposteros Bogotá', 'Insumos generales de repostería'),
        ]
        proveedores_creados = []
        for nombre_emp, desc in proveedores_data:
            prov = Proveedores.objects.create(
                nombre=nombre_emp.split()[0],
                apellido='Proveedor',
                numero=f'31{random.randint(10000000, 99999999)}',
                correo=f'contacto@{nombre_emp.lower().replace(" ", "")[:15]}.com',
                direccion=f'Zona Industrial #{random.randint(1,50)}, Bogotá',
                empresa=nombre_emp,
            )
            proveedores_creados.append(prov)

        self.stdout.write('✅ 5 proveedores creados')

        # ══════════════════════════════════════════════
        # INVENTARIO — 15 registros
        # ══════════════════════════════════════════════
        inventario_data = [
            ('Harina de trigo', 'harinas', 'kg', 50, 10, 3500),
            ('Harina de almendra', 'harinas', 'kg', 20, 5, 18000),
            ('Leche entera', 'lacteos', 'l', 40, 8, 3200),
            ('Crema de leche', 'lacteos', 'l', 25, 5, 9500),
            ('Mantequilla', 'lacteos', 'kg', 30, 6, 14000),
            ('Azúcar blanca', 'endulzantes', 'kg', 60, 15, 2800),
            ('Azúcar pulverizada', 'endulzantes', 'kg', 25, 5, 4200),
            ('Ron añejo', 'licores', 'ml', 3000, 500, 45000),
            ('Fresas', 'frutas', 'kg', 15, 3, 8000),
            ('Maracuyá', 'frutas', 'kg', 10, 2, 6500),
            ('Chocolate negro 70%', 'chocolates', 'kg', 20, 4, 28000),
            ('Chocolate blanco', 'chocolates', 'kg', 15, 3, 26000),
            ('Aceite vegetal', 'aceites', 'l', 20, 5, 7500),
            ('Huevos', 'huevos', 'g', 600, 100, 450),
            ('Frutos rojos mixtos', 'frutos_rojos', 'kg', 12, 3, 15000),
        ]

        for nombre_ing, categoria, unidad, cantidad, stock_min, precio in inventario_data:
            inv = Inventario.objects.create(
                id_proveedor=random.choice(proveedores_creados),
                nombre=nombre_ing,
                descripcion=f'{nombre_ing} de alta calidad para repostería',
                cantidad=cantidad,
                precio_unitario=Decimal(precio),
                stock_minimo=stock_min,
                unidad=unidad,
                categoria=categoria,
            )
            # Movimiento inicial de entrada para que el inventario tenga historial
            Movimiento.objects.create(
                id_inventario=inv,
                cantidad=cantidad,
                tipo='entrada',
                costo_unitario=Decimal(precio),
                observacion='Carga inicial de inventario',
            )

        self.stdout.write('✅ 15 registros de inventario creados (con movimiento de entrada inicial)')

        self.stdout.write(self.style.SUCCESS('🎉 ¡Poblado completo de datos finalizado exitosamente!'))
        self.stdout.write(self.style.SUCCESS(
            f'Resumen: {len(usuarios_creados)} usuarios, 15 productos, 15 solicitudes, '
            f'15 transacciones, 15 PQRS, 5 proveedores, 15 inventario'
        ))