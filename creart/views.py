from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Roles, Permisos, Usuarios, Solicitudes, Productos, PQRS, Transacciones
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count, Sum
import json
from datetime import timedelta
from django.utils.timezone import now
import mercadopago
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')
# Create your views here.

def inicio(request):
    return render(request, 'inicio.html')

#registrar, iniciar y cerrar sesion BACKEND ---------------------------------------
#registrar, iniciar y cerrar sesion BACKEND ---------------------------------------
#registrar, iniciar y cerrar sesion BACKEND ---------------------------------------

def registrar_usuario(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        correo = request.POST['correo']
        numero = request.POST['numero']
        direccion = request.POST['direccion']
        contrasena = make_password(request.POST['contrasena'])

        rol_cliente = Roles.objects.get(nombre="cliente")

        nuevo_usuario = Usuarios.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            numero=numero,
            direccion=direccion,
            contrasena=contrasena,
            rol=rol_cliente
        )

        return redirect('inicio')

    return render(request, 'inicio.html')

def registrar_vendedor(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        correo = request.POST['correo']
        numero = request.POST['numero']
        direccion = request.POST['direccion']
        contrasena = make_password(request.POST['contrasena'])

        rol_vendedor = Roles.objects.get(nombre="vendedor")

        nuevo_usuario = Usuarios.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            numero=numero,
            direccion=direccion,
            contrasena=contrasena,
            rol=rol_vendedor
        )

        return redirect('inicio')

    return render(request, 'inicio.html')

def login_usuario(request):

    if request.method == "POST":

        correo = request.POST['correo']
        contrasena = request.POST['contrasena']

        try:
            usuario = Usuarios.objects.get(correo=correo)

            if not check_password(contrasena, usuario.contrasena):
                return render(request, "inicio.html", {"error": "Contraseña incorrecta"})

            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre

            rol = usuario.rol.nombre
            if rol == "admin":
                return redirect("administrador")
            if rol == "vendedor":
                return redirect("vendedor")
            if rol == "cliente":
                return redirect("cliente")
            # return redirect("catalogo")

        except Usuarios.DoesNotExist:
            return render(request, 'inicio.html', {'error': 'Usuario no existe'})

def cerrar_sesion(request):
    request.session.flush()
    return redirect('inicio')

#admin ----------------------------------------------------------------------
#admin ----------------------------------------------------------------------
#admin ----------------------------------------------------------------------

def administrador(request):
    return render(request, 'administrador.html') 

#vendedor ----------------------------------------------------------------------
#vendedor ----------------------------------------------------------------------
#vendedor ----------------------------------------------------------------------
def vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    vendedor = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    #  Ventas hoy
    hoy = now().date()
    ventas_hoy = Solicitudes.objects.filter(
        producto__vendedor=vendedor,
        fecha_creacion__date=hoy
    ).count()

    # Solicitudes nuevas (últimas)
    solicitudes_nuevas = Solicitudes.objects.filter(
        producto__vendedor=vendedor
    ).order_by('-fecha_creacion')[:3]

    # Clientes activos
    clientes_activos = Usuarios.objects.filter(
        solicitudes__producto__vendedor=vendedor
    ).distinct().count()

    # Productos aprobados
    productos_aprobados = Productos.objects.filter(
        vendedor=vendedor,
        estado_aprobacion='aprobado'
    ).count()

    # Ventas recientes
    ventas = Solicitudes.objects.filter(
        producto__vendedor=vendedor
    ).order_by('-fecha_creacion')[:3]

    return render(request, "vendedor/vendedor.html", {
        "usuario": vendedor,
        "ventas_hoy": ventas_hoy,
        "solicitudes_nuevas": solicitudes_nuevas,
        "clientes_activos": clientes_activos,
        "productos_aprobados": productos_aprobados,
        "ventas": ventas
    })

def solicitudes_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')
    
    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    solicitudes = Solicitudes.objects.filter(producto__vendedor=usuario)

    return render(request, 'solicitudes_vendedor.html', {
        'usuario': usuario,
        'solicitudes': solicitudes
    })

def reportes_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')
    
    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    pendientes = PQRS.objects.filter(
        usuario=usuario,
        estado_respuesta='sin_respuesta'
    )

    respondidos = PQRS.objects.filter(
        usuario=usuario,
        estado_respuesta='respondido'
    )

    return render(request, "reportes_vendedor.html", {
        "usuario": usuario,
        "sin_respuesta": pendientes,
        "respondido": respondidos
    })

def ventas_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    vendedor = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    # 🔥 traer ventas del vendedor
    ventas = Transacciones.objects.filter(
        solicitud__producto__vendedor=vendedor
    ).select_related('solicitud__cliente', 'solicitud__producto')

    # 🔥 estadísticas
    total_ventas = ventas.aggregate(total=Sum('importe_total'))['total'] or 0
    total_pedidos = ventas.count()

    hoy = now().date()
    ventas_hoy = ventas.filter(
        fecha_creacion__date=hoy
    ).count()

    return render(request, 'ventas_vendedor.html', {
        'usuario': vendedor,
        'ventas': ventas,
        'total_ventas': total_ventas,
        'ventas_hoy': ventas_hoy,
        'total_pedidos': total_pedidos
    })

def clientes_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    vendedor = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    clientes = Usuarios.objects.filter(
    solicitudes__producto__vendedor=vendedor
    ).annotate(
        total_compras=Count('solicitudes'),
        total_gastado=Sum('solicitudes__producto__precio')
    ).distinct()

    return render(request, 'vendedor_clientes.html', {
        'usuario': vendedor,
        'clientes': clientes
    })

def productos_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')
    
    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    pendientes = Productos.objects.filter(
        vendedor=usuario,
        estado_aprobacion='pendiente'
    )

    aprobados = Productos.objects.filter(
        vendedor=usuario,
        estado_aprobacion='aprobado'
    )

    return render(request, "productos_vendedor.html", {
        "usuario": usuario,
        "pendientes": pendientes,
        "aprobados": aprobados
    })


def bonos_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    return render(request, 'bonos_vendedor.html', {
        'usuario': usuario
    })

def mi_perfil_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    # Total ventas
    total_ventas = Transacciones.objects.filter(
        solicitud__producto__vendedor=usuario
    ).aggregate(total=Sum('importe_total'))['total'] or 0

    # Total pedidos
    total_pedidos = Solicitudes.objects.filter(
        producto__vendedor=usuario
    ).count()

    # Clientes únicos
    clientes = Usuarios.objects.filter(
        solicitudes__producto__vendedor=usuario
    ).distinct().count()

    # Productos aprobados
    productos_aprobados = Productos.objects.filter(
        vendedor=usuario,
        estado_aprobacion='aprobado'
    ).count()

    return render(request, 'perfil_vendedor.html', {
        'usuario': usuario,
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
        'clientes': clientes,
        'productos_aprobados': productos_aprobados
    })

def soli_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    return render(request, 'hacer_solicitud_vendedor.html', {
        'usuario': usuario
    })

def crear_solicitud_vededor(request):
    clientes = Usuarios.objects.all()
    productos = Productos.objects.all()

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        producto_id = request.POST.get("producto")
        cantidad = request.POST.get("cantidad")
        detalles = request.POST.get("detalles")

        Solicitudes.objects.create(
            cliente_id=cliente_id,
            producto_id=producto_id,
            cantidad=cantidad,
            detalles=detalles
        )

    return render(request, "hacer_Solicitud_vendedor.html", {
        "clientes": clientes,
        "productos": productos
    })
    
def crear_productos(request):
    vendedor = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        precio = request.POST.get("precio")

        Productos.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            vendedor=vendedor,
            estado_aprobacion='pendiente'
        )

    # 🔥 separar productos
    pendientes = Productos.objects.filter(
        vendedor=vendedor,
        estado_aprobacion='pendiente'
    )

    aprobados = Productos.objects.filter(
        vendedor=vendedor,
        estado_aprobacion='aprobado'
    )

    return render(request, "productos_vendedor.html", {
        "pendientes": pendientes,
        "aprobados": aprobados
    })

def editar_perfil_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    if request.method == "POST":

        datos = {
            "nombre": request.POST.get('nombre'),
            "apellido": request.POST.get('apellido'),
            "correo": request.POST.get('correo'),
            "numero": request.POST.get('numero'),
            "direccion": request.POST.get('direccion')
        }

        PQRS.objects.create(
            usuario=usuario,
            asunto="Solicitud cambio de perfil",
            mensaje=json.dumps(datos),
            categoria='solicitud',
            estado_respuesta='sin_respuesta'
        )

        return redirect('vendedor_perfil')
    
def crear_reporte_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    vendedor = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    datos = {
    "Nombre": request.POST.get('nombre'),
    "Apellido": request.POST.get('apellido'),
    "Correo": request.POST.get('correo'),
    "Número": request.POST.get('numero'),
    "Dirección": request.POST.get('direccion')
    }

    mensaje = ""

    for campo, valor in datos.items():
        if valor:  # solo los que sí tengan valor
            mensaje += f"{campo}: {valor}\n"

    PQRS.objects.create(
        usuario=vendedor,
        asunto="Solicitud cambio de perfil",
        mensaje=mensaje,
        categoria='solicitud',
        estado_respuesta='sin_respuesta'
    )

    print("REPORTE GUARDADO")

    return redirect('vendedor_reportes')

    pendientes = PQRS.objects.filter(
        usuario=vendedor,
        estado_respuesta='sin_respuesta'
    )

    respondidos = PQRS.objects.filter(
        usuario=vendedor,
        estado_respuesta='respondido'
    )

    for p in pendientes:
        if p.categoria == 'solicitud':
            try:
                p.mensaje_json = json.loads(p.mensaje)
            except:
                p.mensaje_json = None

    return render(request, "reportes_vendedor.html", {
        "usuario": vendedor,
        "sin_respuesta": pendientes,
        "respondidos": respondidos
    })

# cliente -----------------------------------------------------------------------------
# cliente -----------------------------------------------------------------------------
# cliente -----------------------------------------------------------------------------

def inicio_cliente(request):
    pasteles = Productos.objects.all()[:6]
    return render(request, "inicio_cliente.html", {"pasteles": pasteles})


def catalogo(request):
    categoria = request.GET.get("categoria", "todos")
    pasteles = (
        Productos.objects.filter(categoria=categoria)
        if categoria != "todos"
        else Productos.objects.all()
    )
    return render(request, "catalogo.html", {
        "pasteles": pasteles,
        "categoria_activa": categoria,
        "total": pasteles.count(),
    })


def compra_rapida(request, producto_id):
    producto = get_object_or_404(Productos, id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'compra_rapida.html', {
        'producto': producto,
        'usuario': usuario,
    })


# ─────────────────────────────────────────
# CONFIGURADOR
# ─────────────────────────────────────────

def configurador(request, producto_id):
    producto = get_object_or_404(Productos, id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'configurador.html', {
        'producto': producto,
        'usuario': usuario,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
    })


# ─────────────────────────────────────────
# SOLICITUDES (CLIENTE)
# ─────────────────────────────────────────

def crear_solicitud(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo')

    producto = get_object_or_404(Productos, id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None

    precio_total = int(float(request.POST.get('precio_total', producto.precio)))

    solicitud = Solicitudes.objects.create(
        usuario=usuario,
        producto=producto,
        nombre_invitado=request.POST.get('nombre_invitado', ''),
        direccion_entrega=request.POST.get('direccion_entrega', ''),
        tipo_entrega=request.POST.get('tipo_entrega', 'tienda'),
        mensaje_pastel=request.POST.get('mensaje_pastel', ''),
        cobertura=request.POST.get('cobertura', 'chantilly'),
        rellenos=request.POST.get('rellenos', ''),
        decoracion=request.POST.get('decoracion', ''),
        pisos=int(request.POST.get('pisos', 1)),
        porciones=request.POST.get('porciones', 2),
        precio_total=precio_total,
        fecha_evento=request.POST.get('fecha_evento') or None,
        estado='pendiente',
    )

    # Productos de eventos no pasan por pasarela de pago inmediata
    if producto.categoria == 'eventos':
        return redirect('solicitud_pendiente', solicitud_id=solicitud.id_solicitud)

    return _redirigir_a_mercadopago(solicitud, usuario, producto, precio_total)


def mis_solicitudes(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')

    estado = request.GET.get('estado', 'todos')
    solicitudes = Solicitudes.objects.filter(usuario_id=usuario_id).order_by('-fecha_solicitud')
    if estado != 'todos':
        solicitudes = solicitudes.filter(estado=estado)

    return render(request, 'mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'estado_activo': estado,
    })


def detalle_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('inicio')
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'detalle_solicitud.html', {'solicitud': solicitud})


def cancelar_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('inicio')
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    if solicitud.estado == 'pendiente':
        solicitud.estado = 'rechazada'
        solicitud.save()
    return redirect('mis_solicitudes')


def solicitud_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'solicitud_pendiente.html', {'solicitud': solicitud})


# ─────────────────────────────────────────
# MERCADOPAGO — PAGOS
# ─────────────────────────────────────────

def _redirigir_a_mercadopago(solicitud, usuario, producto, precio_total):
    """Helper interno: crea una preferencia MP y redirige al init_point."""
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    nombre_comprador = usuario.nombre if usuario else solicitud.nombre_invitado

    preference_data = {
        "items": [{
            "title": producto.nombre,
            "quantity": 1,
            "unit_price": precio_total,
            "currency_id": "COP",
        }],
        "payer": {"name": nombre_comprador},
        "back_urls": {
            "success": "https://www.google.com",
            "failure": "https://www.google.com",
            "pending": "https://www.google.com",
        },
        "external_reference": str(solicitud.id_solicitud),
    }

    preference = sdk.preference().create(preference_data)

    if "id" not in preference["response"]:
        print("ERROR MP:", preference["response"])
        return HttpResponse(f"Error MercadoPago: {preference['response']}", status=500)

    solicitud.mp_preference_id = preference["response"]["id"]
    solicitud.save()

    return redirect(preference["response"]["init_point"])

def pagar_abono(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('inicio')

    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"Abono — {solicitud.producto.nombre}",
            "quantity": 1,
            "unit_price": float(solicitud.abono),
            "currency_id": "COP",
        }],
        "back_urls": {
            "success": "https://www.google.com",
            "failure": "https://www.google.com",
            "pending": "https://www.google.com",
        },
        "external_reference": str(solicitud.id_solicitud),
    }

    preference = sdk.preference().create(preference_data)
    return redirect(preference["response"]["sandbox_init_point"])


def pago_exitoso(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    solicitud.estado = 'pagada'
    solicitud.save()
    return render(request, 'pago_exitoso.html', {'solicitud': solicitud})


def pago_fallido(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'pago_fallido.html', {'solicitud': solicitud})


def pago_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'pago_pendiente.html', {'solicitud': solicitud})


# ─────────────────────────────────────────
# MERCADOPAGO — WEBHOOK
# ─────────────────────────────────────────

@csrf_exempt
def webhook_mp(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
        if data.get('type') != 'payment':
            return HttpResponse(status=200)

        payment_id = data['data']['id']
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        info = sdk.payment().get(payment_id)['response']

        solicitud = get_object_or_404(Solicitudes, id_solicitud=info.get('external_reference'))
        solicitud.mp_payment_id = str(payment_id)

        if info.get('status') == 'approved':
            solicitud.estado = 'pagada'
            solicitud.save()
            Transacciones.objects.create(
                solicitud=solicitud,
                importe_total=solicitud.precio_total,
                moneda='COP',
                estado='aprobada',
                metodo_pago=info.get('payment_method_id', ''),
                mp_payment_id=str(payment_id),
            )
        else:
            solicitud.estado = 'pendiente'
            solicitud.save()

    except Exception as e:
        print(f"Webhook error: {e}")

    return HttpResponse(status=200)
