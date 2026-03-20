from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
import mercadopago
import json

from .models import Usuarios, Roles, Productos, Solicitud, Transaccion

# ─────────────────────────────────────────
# PÁGINAS GENERALES
# ─────────────────────────────────────────

def index(request):
    return render(request, 'index.html')

def inicio(request):
    return render(request, 'inicio.html')

def administrador(request):
    return render(request, 'administrador.html')

def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

def login_usuario(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        usuario = Usuarios.objects.filter(correo=correo, contraseña=contrasena).first()
        if usuario:
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre
            if usuario.rol.nombre == "admin":
                return redirect("administrador")
            return redirect("catalogo")
        return render(request, "inicio.html", {"error": "Correo o contraseña incorrectos"})
    return render(request, "inicio.html")

def register_usuario(request):
    if request.method == "POST":
        rol_cliente = Roles.objects.get(nombre="cliente")
        Usuarios.objects.create(
            documento=request.POST.get("documento"),
            nombre=request.POST.get("nombre"),
            apellido=request.POST.get("apellido"),
            correo=request.POST.get("correo"),
            numero_telefono=request.POST.get("numero"),
            direccion=request.POST.get("direccion"),
            contraseña=request.POST.get("contrasena"),
            rol=rol_cliente
        )
        return redirect("inicio")
    return render(request, "inicio.html")

def cerrar_sesion(request):
    request.session.flush()
    return redirect("index")

# ─────────────────────────────────────────
# CLIENTE
# ─────────────────────────────────────────

def inicio_cliente(request):
    pasteles = Productos.objects.all()[:6]
    return render(request, "inicio_cliente.html", {"pasteles": pasteles})

def catalogo(request):
    categoria = request.GET.get("categoria", "todos")
    pasteles = Productos.objects.filter(categoria=categoria) if categoria != "todos" else Productos.objects.all()
    return render(request, "catalogo.html", {
        "pasteles": pasteles,
        "categoria_activa": categoria,
        "total": pasteles.count()
    })

def compra_rapida(request, producto_id):
    producto = Productos.objects.get(id_producto=producto_id)
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
    producto = Productos.objects.get(id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'configurador.html', {
        'producto': producto,
        'usuario': usuario,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
    })

# ─────────────────────────────────────────
# CREAR SOLICITUD + MERCADOPAGO
# ─────────────────────────────────────────

def crear_solicitud(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo')

    producto = Productos.objects.get(id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None

    nombre_invitado = request.POST.get('nombre_invitado', '')
    direccion = request.POST.get('direccion_entrega', '')
    tipo_entrega = request.POST.get('tipo_entrega', 'tienda')
    mensaje_pastel = request.POST.get('mensaje_pastel', '')
    cobertura = request.POST.get('cobertura', 'chantilly')
    rellenos = request.POST.get('rellenos', '')
    decoracion = request.POST.get('decoracion', '')
    pisos = int(request.POST.get('pisos', 1))
    porciones = request.POST.get('porciones', 2)
    precio_total = int(float(request.POST.get('precio_total', producto.precio)))
    fecha_evento = request.POST.get('fecha_evento') or None

    solicitud = Solicitud.objects.create(
        usuario=usuario,
        producto=producto,
        nombre_invitado=nombre_invitado,
        direccion_entrega=direccion,
        tipo_entrega=tipo_entrega,
        mensaje_pastel=mensaje_pastel,
        cobertura=cobertura,
        rellenos=rellenos,
        decoracion=decoracion,
        pisos=pisos,
        porciones=porciones,
        precio_total=precio_total,
        fecha_evento=fecha_evento,
        estado='pendiente',
    )

    if producto.categoria == 'eventos':
        return redirect('solicitud_pendiente', solicitud_id=solicitud.id_solicitud)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    nombre_comprador = usuario.nombre if usuario else nombre_invitado

    preference_data = {
        "items": [
            {
                "title": f"{producto.nombre}",
                "quantity": 1,
                "unit_price": precio_total,
                "currency_id": "COP",
            }
        ],
        "payer": {
            "name": nombre_comprador,
        },
        "back_urls": {
            "success": "https://www.google.com",
            "failure": "https://www.google.com",
            "pending": "https://www.google.com",
        },
        "external_reference": str(solicitud.id_solicitud),
    }

    preference = sdk.preference().create(preference_data)
    print("RESPUESTA MP:", preference)

    if "id" not in preference["response"]:
        print("ERROR MP:", preference["response"])
        return HttpResponse(f"Error MercadoPago: {preference['response']}", status=500)

    solicitud.mp_preference_id = preference["response"]["id"]
    solicitud.save()

    init_point = preference["response"]["init_point"]  # pruebas
    # init_point = preference["response"]["init_point"]        # producción
    return redirect(init_point)

# ─────────────────────────────────────────
# WEBHOOK MERCADOPAGO
# ─────────────────────────────────────────

@csrf_exempt
def webhook_mp(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        data = json.loads(request.body)
        if data.get('type') == 'payment':
            payment_id = data['data']['id']
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment = sdk.payment().get(payment_id)
            info = payment['response']
            solicitud_id = info.get('external_reference')
            estado_mp = info.get('status')
            solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
            solicitud.mp_payment_id = str(payment_id)
            if estado_mp == 'approved':
                solicitud.estado = 'pagada'
                solicitud.save()
                Transaccion.objects.create(
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

# ─────────────────────────────────────────
# RETORNO MERCADOPAGO
# ─────────────────────────────────────────

def pago_exitoso(request, solicitud_id):
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    solicitud.estado = 'pagada'
    solicitud.save()
    return render(request, 'pago_exitoso.html', {'solicitud': solicitud})

def pago_fallido(request, solicitud_id):
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    return render(request, 'pago_fallido.html', {'solicitud': solicitud})

def pago_pendiente(request, solicitud_id):
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    return render(request, 'pago_pendiente.html', {'solicitud': solicitud})

def solicitud_pendiente(request, solicitud_id):
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    return render(request, 'solicitud_pendiente.html', {'solicitud': solicitud})

# ─────────────────────────────────────────
# MIS SOLICITUDES
# ─────────────────────────────────────────

def mis_solicitudes(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')
    estado = request.GET.get('estado', 'todos')
    solicitudes = Solicitud.objects.filter(usuario_id=usuario_id).order_by('-fecha_solicitud')
    if estado != 'todos':
        solicitudes = solicitudes.filter(estado=estado)
    return render(request, 'mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'estado_activo': estado,
    })

def detalle_solicitud(request, solicitud_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    return render(request, 'detalle_solicitud.html', {'solicitud': solicitud})

def cancelar_solicitud(request, solicitud_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    if solicitud.estado == 'pendiente':
        solicitud.estado = 'rechazada'
        solicitud.save()
    return redirect('mis_solicitudes')

def pagar_abono(request, solicitud_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')
    solicitud = Solicitud.objects.get(id_solicitud=solicitud_id)
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    preference_data = {
        "items": [
            {
                "title": f"Abono — {solicitud.producto.nombre}",
                "quantity": 1,
                "unit_price": float(solicitud.abono),
                "currency_id": "COP",
            }
        ],
        "back_urls": {
            "success": "https://www.google.com",
            "failure": "https://www.google.com",
            "pending": "https://www.google.com",
        },
        "external_reference": str(solicitud.id_solicitud),
    }
    preference = sdk.preference().create(preference_data)
    init_point = preference["response"]["sandbox_init_point"]
    return redirect(init_point)