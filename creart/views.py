from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count, Sum, Avg, Q
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
import mercadopago
from datetime import timedelta
import json

from .models import Roles, Permisos, Usuarios, Solicitudes, Productos, PQRS, Transacciones


# ═══════════════════════════════════════════════════════════════════
#  PÁGINAS GENERALES
# ═══════════════════════════════════════════════════════════════════

def index(request):
    return render(request, 'index.html')

def inicio(request):
    return render(request, 'inicio.html')


# ═══════════════════════════════════════════════════════════════════
#  PROTECTORES DE SESIÓN
# ═══════════════════════════════════════════════════════════════════

def login_requerido(vista):
    """Redirige al login si no hay sesión activa."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('inicio')
        return vista(request, *args, **kwargs)
    wrapper.__name__ = vista.__name__
    return wrapper


def get_usuario_sesion(request):
    """Retorna el objeto Usuarios de la sesión activa o None."""
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            return Usuarios.objects.select_related('rol').get(pk=usuario_id)
        except Usuarios.DoesNotExist:
            pass
    return None


# ═══════════════════════════════════════════════════════════════════
#  AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════

def registrar_usuario(request):
    """Registra un nuevo usuario con rol 'cliente'."""
    if request.method != "POST":
        return render(request, "inicio.html")

    rol_cliente = Roles.objects.get(nombre="cliente")
    Usuarios.objects.create(
        nombre=request.POST.get("nombre"),
        apellido=request.POST.get("apellido"),
        correo=request.POST.get("correo"),
        numero=request.POST.get("numero"),
        direccion=request.POST.get("direccion", ""),
        contrasena=make_password(request.POST.get("contrasena")),
        rol=rol_cliente,
    )
    return redirect("inicio")


def registrar_vendedor(request):
    """Registra un nuevo usuario con rol 'vendedor'."""
    if request.method != "POST":
        return render(request, "inicio.html")

    rol_vendedor = Roles.objects.get(nombre="vendedor")
    Usuarios.objects.create(
        nombre=request.POST.get("nombre"),
        apellido=request.POST.get("apellido"),
        correo=request.POST.get("correo"),
        numero=request.POST.get("numero"),
        direccion=request.POST.get("direccion", ""),
        contrasena=make_password(request.POST.get("contrasena")),
        rol=rol_vendedor,
    )
    return redirect("inicio")


def login_usuario(request):
    #Autentica al usuario por correo y contraseña hasheada.
    if request.method != "POST":
        return render(request, "inicio.html")

    correo = request.POST.get("correo")
    contrasena = request.POST.get("contrasena")

    try:
        usuario = Usuarios.objects.get(correo=correo)

        if not check_password(contrasena, usuario.contrasena):
            return render(request, "inicio.html", {"error": "Contraseña incorrecta"})

        request.session['usuario_id'] = usuario.id_usuario
        request.session['usuario_nombre'] = usuario.nombre

        rol = usuario.rol.nombre
        if rol == "administrador":
            return redirect("administrador")
        if rol == "vendedor":
            return redirect("vendedor")
        if rol == "cliente":
            return redirect("catalogo")

    except Usuarios.DoesNotExist:
        return render(request, 'inicio.html', {'error': 'Usuario no existe'})


def cerrar_sesion(request):
    request.session.flush()
    return redirect('inicio')


# ═══════════════════════════════════════════════════════════════════
#  ADMINISTRADOR
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def administrador(request):
    usuario = get_usuario_sesion(request)

    ventas_totales = Transacciones.objects.aggregate(
        total=Sum('importe_total'))['total'] or 0
 
    pedidos_total = Transacciones.objects.count()

    clientes_total = Usuarios.objects.filter(
        rol__nombre__iexact='cliente').count()

    promedio_venta = Transacciones.objects.aggregate(
        prom=Avg('importe_total'))['prom'] or 0

    transacciones_recientes = (
        Transacciones.objects
        .select_related('solicitud__usuarios')
        .order_by('-fecha_creacion')[:5]
    )

    hoy = timezone.now()
    ventas_mensuales = []
    pedidos_mensuales = []

    for i in range(5, -1, -1):
        fecha = hoy - timedelta(days=30 * i)
        mes_inicio = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        siguiente = fecha.replace(day=28) + timedelta(days=4)
        mes_fin = siguiente.replace(day=1) if i != 0 else hoy

        total = Transacciones.objects.filter(
            fecha_creacion__gte=mes_inicio,
            fecha_creacion__lt=mes_fin
        ).aggregate(total=Sum('importe_total'))['total'] or 0

        count = Transacciones.objects.filter(
            fecha_creacion__gte=mes_inicio,
            fecha_creacion__lt=mes_fin
        ).count()

        ventas_mensuales.append({'mes': fecha.strftime('%b'), 'total': float(total)})
        pedidos_mensuales.append({'mes': fecha.strftime('%b'), 'count': count})

    productos_top = (
        Productos.objects
        .annotate(total_vendido=Sum('solicitudes__porciones'))
        .order_by('-total_vendido')[:5]
    )

    clientes_top = (
        Usuarios.objects
        .filter(rol__nombre__iexact='cliente')
        .annotate(
            num_pedidos=Count('solicitudes'),
            total_gastado=Sum('solicitudes__transacciones__importe_total')
        )
        .order_by('-num_pedidos')[:5]
    )

    context = {
        'usuario': usuario,
        'ventas_totales': ventas_totales,
        'pedidos_total': pedidos_total,
        'clientes_total': clientes_total,
        'promedio_venta': round(float(promedio_venta), 2),
        'transacciones_recientes': transacciones_recientes,
        'ventas_mensuales_json': json.dumps(ventas_mensuales),
        'pedidos_mensuales': pedidos_mensuales,
        'productos_top': productos_top,
        'clientes_top': clientes_top,
        'pagina_activa': 'administrador',
    }
    return render(request, 'administrador/administrador.html', context)


# ═══════════════════════════════════════════════════════════════════
#  USUARIOS (ADMIN)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def usuarios(request):
    usuario = get_usuario_sesion(request)

    q = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()

    qs = Usuarios.objects.select_related('Roles').all()

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(correo__icontains=q) |
            Q(documento__icontains=q)
        )

    if rol_filtro:
        qs = qs.filter(rol__nombre__iexact=rol_filtro)

    context = {
        'usuario': usuario,
        'usuarios': qs,
        'total_usuarios': Usuarios.objects.count(),
        'roles': Roles.objects.all(),
        'q': q,
        'rol_filtro': rol_filtro,
        'pagina_activa': 'usuarios',
    }
    return render(request, 'administrador/usuarios.html', context)


# ═══════════════════════════════════════════════════════════════════
#  TRANSACCIONES (ADMIN)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def transacciones(request):
    usuario = get_usuario_sesion(request)

    q = request.GET.get('q', '').strip()

    qs = Transacciones.objects.select_related(
        'solicitud__usuarios'
    ).order_by('-fecha_creacion')

    if q:
        qs = qs.filter(
            Q(id_pedido__icontains=q) |
            Q(solicitud__Usuarios__nombre__icontains=q) |
            Q(solicitud__Usuarios__apellido__icontains=q)
        )

    total_tx = Transacciones.objects.count()

    context = {
        'usuario': usuario,
        'transacciones': qs,
        'completadas': total_tx,
        'pendientes': 0,
        'devueltas': 0,
        'total_tx': total_tx,
        'q': q,
        'pagina_activa': 'transacciones',
    }
    return render(request, 'administrador/transacciones.html', context)

# ═══════════════════════════════════════════════════════════════════
#  PRODUCTOS (ADMIN)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def productos(request):
    usuarios = get_usuario_sesion(request)

    q = request.GET.get('q', '').strip()

    qs = Productos.objects.select_related('vendedor')\
    .filter(estado=True)\
    .order_by('-fecha_creacion')

    if q:
        qs = qs.filter(
            Q(id_producto__icontains=q) |
            Q(vendedor__nombre__icontains=q) |
            Q(vendedor__apellido__icontains=q)
        )

    pendientes = Productos.objects.filter(estado_aprobacion='pendiente').count()
    aprobados = Productos.objects.filter(estado_aprobacion='aprobado').count()
    rechazados = Productos.objects.filter(estado_aprobacion='rechazado').count()
    inactivos = Productos.objects.filter(estado=False).order_by('-fecha_creacion')
    total_tx = Productos.objects.count()

    context = {
        'usuario': usuarios,
        'inactivos': inactivos,
        'productos': qs,
        'pendientes': pendientes,
        'aprobados': aprobados,
        'rechazados': rechazados,
        'total_tx': total_tx,
    }

    return render(request, 'administrador/productos.html', context)

#acciones ------------------------------>
#acciones ------------------------------>

@login_requerido
def cambiar_estado_producto(request, id_producto):
    if request.method == "POST":
        producto = Productos.objects.get(id_producto=id_producto)

        accion = request.POST.get("accion")

        if accion == "aprobar":
            producto.estado_aprobacion = "aprobado"

        elif accion == "rechazar":
            producto.estado_aprobacion = "rechazado"
            producto.motivo_rechazo = request.POST.get("motivo", "")

        producto.save()

    return redirect("productos")


# ═══════════════════════════════════════════════════════════════════
#  SOLICITUDES (ADMIN)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def solicitudes(request):
    usuario = get_usuario_sesion(request)

    q = request.GET.get('q', '').strip()

    qs = Solicitudes.objects.select_related(
        'solicitudes__usuarios'
    ).order_by('-fecha_creacion')

    if q:
        qs = qs.filter(
            Q(id_pedido__icontains=q) |
            Q(solicitud__Usuarios__nombre__icontains=q) |
            Q(solicitud__Usuarios__apellido__icontains=q)
        )

    total_tx = Transacciones.objects.count()

    context = {
        'usuario': usuario,
        'transacciones': qs,
        'completadas': total_tx,
        'pendientes': 0,
        'devueltas': 0,
        'total_tx': total_tx,
        'q': q,
        'pagina_activa': 'transacciones',
    }
    return render(request, 'administrador/transacciones.html', context)


# ═══════════════════════════════════════════════════════════════════
#  PQRS (ADMIN)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def pqrs(request):
    usuario = get_usuario_sesion(request)

    qs = PQRS.objects.select_related('usuario').order_by('-id_pqrs')

    context = {
        'usuario': usuario,
        'pqrs_list': qs,
        'total_pqrs': qs.count(),
        'pendientes': qs.count(),
        'en_proceso': 0,
        'resueltos': 0,
        'pagina_activa': 'pqrs',
    }
    return render(request, 'administrador/pqrs.html', context)


@login_requerido
def pqrs_responder(request, pk):
    if request.method == 'POST':
        pqrs_obj = get_object_or_404(PQRS, pk=pk)
        # pqrs_obj.respuesta = request.POST.get('respuesta', '')
        # pqrs_obj.save()
    return redirect('pqrs')


# ═══════════════════════════════════════════════════════════════════
#  PERFIL (ADMIN)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
def administrador_perfil(request):
    usuario = get_usuario_sesion(request)

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre', usuario.nombre)
        usuario.apellido = request.POST.get('apellido', usuario.apellido)
        usuario.correo = request.POST.get('correo', usuario.correo)
        usuario.numero = request.POST.get('numero', usuario.numero)
        usuario.direccion = request.POST.get('direccion', usuario.direccion)

        nueva = request.POST.get('nueva_contrasena', '').strip()
        if nueva:
            usuario.contrasena = make_password(nueva)

        usuario.save()
        request.session['usuario_nombre'] = usuario.nombre
        return redirect('administrador_perfil')

    context = {
        'usuario': usuario,
        'pagina_activa': 'perfil',
    }
    return render(request, 'administrador/administrador_perfil.html', context)


# ═══════════════════════════════════════════════════════════════════
#  VENDEDOR
# ═══════════════════════════════════════════════════════════════════

def _get_vendedor(request):
    """Helper interno: retorna el usuario vendedor de la sesión o None."""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None
    try:
        return Usuarios.objects.get(id_usuario=usuario_id)
    except Usuarios.DoesNotExist:
        return None


@login_requerido
def vendedor(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')

    # Ventas hoy
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


@login_requerido
def solicitudes_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    solicitudes = Solicitudes.objects.filter(producto__vendedor=usuario)

    return render(request, 'vendedor/solicitudes_vendedor.html', {
        'usuario': usuario,
        'solicitudes': solicitudes
    })


@login_requerido
def reportes_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    pendientes = PQRS.objects.filter(
        usuario=usuario,
        estado_respuesta='sin_respuesta'
    )

    respondidos = PQRS.objects.filter(
        usuario=usuario,
        estado_respuesta='respondido'
    )

    return render(request, "vendedor/reportes_vendedor.html", {
        "usuario": usuario,
        "sin_respuesta": pendientes,
        "respondido": respondidos
    })


@login_requerido
def ventas_vendedor(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')

    # Traer ventas del vendedor
    ventas = Transacciones.objects.filter(
        solicitud__producto__vendedor=vendedor
    ).select_related('solicitud__usuario', 'solicitud__producto')

    # Estadísticas
    total_ventas = ventas.aggregate(total=Sum('importe_total'))['total'] or 0
    total_pedidos = ventas.count()

    hoy = now().date()
    ventas_hoy = ventas.filter(
        fecha_creacion__date=hoy
    ).count()

    return render(request, 'vendedor/ventas_vendedor.html', {
        'usuario': vendedor,
        'ventas': ventas,
        'total_ventas': total_ventas,
        'ventas_hoy': ventas_hoy,
        'total_pedidos': total_pedidos
    })


@login_requerido
def clientes_vendedor(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')

    clientes = Usuarios.objects.filter(
        solicitudes__producto__vendedor=vendedor
    ).annotate(
        total_compras=Count('solicitudes'),
        total_gastado=Sum('solicitudes__producto__precio')
    ).distinct()

    return render(request, 'vendedor/vendedor_clientes.html', {
        'usuario': vendedor,
        'clientes': clientes
    })


@login_requerido
def productos_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    if request.method == "POST":
        Productos.objects.create(
            nombre=request.POST.get("nombre"),
            descripcion=request.POST.get("descripcion"),
            precio=request.POST.get("precio"),
            imagen=request.POST.get("imagen"),
            vendedor=usuario,
            estado_aprobacion='pendiente',
        )

    pendientes = Productos.objects.filter(
        vendedor=usuario,
        estado_aprobacion='pendiente',
        estado=True
    )

    aprobados = Productos.objects.filter(
        vendedor=usuario,
        estado_aprobacion='aprobado',
        estado=True
    )

    rechazados = Productos.objects.filter(
        vendedor=usuario,
        estado_aprobacion='rechazado',
        estado=True
    )

    return render(request, "vendedor/productos_vendedor.html", {
        "usuario": usuario,
        "pendientes": pendientes,
        "aprobados": aprobados,
        "rechazados": rechazados
    })


@login_requerido
def bonos_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    return render(request, 'vendedor/bonos_vendedor.html', {
        'usuario': usuario
    })


@login_requerido
def mi_perfil_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

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

    return render(request, 'vendedor/perfil_vendedor.html', {
        'usuario': usuario,
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
        'clientes': clientes,
        'productos_aprobados': productos_aprobados
    })


@login_requerido
def soli_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    return render(request, 'vendedor/hacer_solicitud_vendedor.html', {
        'usuario': usuario
    })

#acciones ---------------------------------------------------------------------->
#acciones ---------------------------------------------------------------------->
#acciones ---------------------------------------------------------------------->

@login_requerido
def cambiar_estado_producto_vendedor(request, id_producto):
    if request.method == "POST":
        producto = Productos.objects.get(id_producto=id_producto)

        # invertir el estado
        producto.estado = not producto.estado

        producto.save()

    return redirect("vendedor_productos")

@login_requerido
def editar_producto_vendedor(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)

    if request.method == "POST":
        producto.nombre = request.POST.get("nombre")
        producto.descripcion = request.POST.get("descripcion")
        producto.precio = request.POST.get("precio")
        producto.categoria = request.POST.get("categoria")
        if request.FILES.get("imagen"):
            producto.imagen = request.FILES.get("imagen")
        producto.save()

        return redirect('vendedor_productos')  # tu vista principal

    return redirect('vendedor_productos')

@login_requerido
def crear_solicitud_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    if request.method == "POST":
        Solicitudes.objects.create(
            cliente_id=request.POST.get("cliente"),
            producto_id=request.POST.get("producto"),
            cantidad=request.POST.get("cantidad"),
            detalles=request.POST.get("detalles"),
        )

    return render(request, "vendedor/hacer_solicitud_vendedor.html", {
        "usuario": usuario,
        "clientes": Usuarios.objects.all(),
        "productos": Productos.objects.all(),
    })


@login_requerido
def crear_productos(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')

    if request.method == "POST":
        Productos.objects.create(
            nombre=request.POST.get("nombre"),
            descripcion=request.POST.get("descripcion"),
            precio=request.POST.get("precio"),
            imagen=request.POST.get("imagen"),
            vendedor=vendedor,
            categoria=request.POST.get("categoria"),
            estado_aprobacion='pendiente'
        )

    return redirect("vendedor_productos")


@login_requerido
def editar_perfil_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

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


@login_requerido
def crear_reporte_vendedor(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')

    if request.method == "POST":
        datos = {
            "Nombre": request.POST.get('nombre'),
            "Apellido": request.POST.get('apellido'),
            "Correo": request.POST.get('correo'),
            "Número": request.POST.get('numero'),
            "Dirección": request.POST.get('direccion')
        }

        mensaje = ""
        for campo, valor in datos.items():
            if valor:
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

    return render(request, "vendedor/reportes_vendedor.html", {
        "usuario": vendedor,
        "sin_respuesta": pendientes,
        "respondidos": respondidos
    })


# ═══════════════════════════════════════════════════════════════════
#  CLIENTE
# ═══════════════════════════════════════════════════════════════════

def catalogo(request):
    categoria = request.GET.get("categoria", "todos")
    pasteles = (
        Productos.objects.filter(categoria=categoria, estado=True)
        if categoria != "todos"
        else Productos.objects.filter(estado=True)
    )
    return render(request, "cliente/catalogo.html", {
        "pasteles": pasteles,
        "categoria_activa": categoria,
        "total": pasteles.count(),
    })


def compra_rapida(request, producto_id):
    producto = get_object_or_404(Productos, id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'cliente/compra_rapida.html', {
        'producto': producto,
        'usuario': usuario,
    })


# ═══════════════════════════════════════════════════════════════════
#  CONFIGURADOR
# ═══════════════════════════════════════════════════════════════════

def configurador(request, producto_id):
    producto = get_object_or_404(Productos, id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'cliente/configurador.html', {
        'producto': producto,
        'usuario': usuario,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
    })


# ═══════════════════════════════════════════════════════════════════
#  SOLICITUDES (CLIENTE)
# ═══════════════════════════════════════════════════════════════════

@login_requerido
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


@login_requerido
def mis_solicitudes(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')

    estado = request.GET.get('estado', 'todos')
    solicitudes = Solicitudes.objects.filter(usuario_id=usuario_id).order_by('-fecha_solicitud')
    if estado != 'todos':
        solicitudes = solicitudes.filter(estado=estado)

    return render(request, 'cliente/mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'estado_activo': estado,
    })


@login_requerido
def detalle_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('inicio')
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'detalle_solicitud.html', {'solicitud': solicitud})


@login_requerido
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
    return render(request, 'cliente/solicitud_pendiente.html', {'solicitud': solicitud})


# ═══════════════════════════════════════════════════════════════════
#  MERCADOPAGO — PAGOS
# ═══════════════════════════════════════════════════════════════════

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


@login_requerido
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
    return render(request, 'cliente/pago_exitoso.html', {'solicitud': solicitud})


def pago_fallido(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'cliente/pago_fallido.html', {'solicitud': solicitud})


def pago_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    return render(request, 'cliente/pago_pendiente.html', {'solicitud': solicitud})


# ═══════════════════════════════════════════════════════════════════
#  MERCADOPAGO — WEBHOOK
# ═══════════════════════════════════════════════════════════════════

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