from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Roles, Usuarios, Solicitud, Producto, PQRS, Transaccion


# ═══════════════════════════════════════════
#  DECORADOR — protege vistas del admin
# ═══════════════════════════════════════════
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
            return Usuarios.objects.select_related('Roles').get(pk=usuario_id)
        except Usuarios.DoesNotExist:
            pass
    return None


# ═══════════════════════════════════════════
#  PÁGINAS PÚBLICAS
# ═══════════════════════════════════════════
def index(request):
    return render(request, 'index.html')


def inicio(request):
    """Página de login/registro — si ya hay sesión redirige al panel."""
    if request.session.get('usuario_id'):
        usuario = get_usuario_sesion(request)
        if usuario:
            rol = usuario.Roles.nombre.lower()
            if rol == 'administrador':
                return redirect('administrador')
            else:
                return redirect('vendedor')
    return render(request, 'inicio.html')


# ═══════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════
def login(request):
    if request.method == 'POST':
        correo     = request.POST.get('correo', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()

        try:
            usuario = Usuarios.objects.select_related('Roles').get(correo=correo)

            if usuario.contrasena == contrasena:
                # Guardar sesión
                request.session['usuario_id']     = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_rol']    = usuario.Roles.nombre

                # Redirigir según rol
                rol = usuario.Roles.nombre.lower()
                if rol == 'administrador':
                    return redirect('administrador')
                else:
                    return redirect('vendedor')
            else:
                return render(request, 'inicio.html', {
                    'error': 'Correo o contraseña incorrectos.'
                })

        except Usuarios.DoesNotExist:
            return render(request, 'inicio.html', {
                'error': 'Correo o contraseña incorrectos.'
            })

    return redirect('inicio')


# ═══════════════════════════════════════════
#  REGISTRO
# ═══════════════════════════════════════════
def register(request):
    if request.method == 'POST':
        try:
            rol_cliente = Roles.objects.get(nombre__iexact='cliente')
            usuario = Usuarios(
                documento  = request.POST.get('documento', ''),
                nombre     = request.POST.get('nombre', ''),
                apellido   = request.POST.get('apellido', ''),
                correo     = request.POST.get('correo', ''),
                numero     = request.POST.get('numero', ''),
                direccion  = request.POST.get('direccion', ''),
                contrasena = request.POST.get('contrasena', ''),
                Roles      = rol_cliente,
            )
            usuario.save()
            return redirect('inicio')

        except Roles.DoesNotExist:
            return render(request, 'inicio.html', {
                'error_register': 'No existe el rol cliente. Contacta al administrador.'
            })
        except Exception as e:
            return render(request, 'inicio.html', {
                'error_register': f'Error al registrar: {str(e)}'
            })

    return redirect('inicio')


# ═══════════════════════════════════════════
#  CERRAR SESIÓN
# ═══════════════════════════════════════════
def cerrar_sesion(request):
    request.session.flush()
    return redirect('inicio')


# ═══════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════
@login_requerido
def administrador(request):
    usuario = get_usuario_sesion(request)

    ventas_totales = Transaccion.objects.aggregate(
        total=Sum('importe_total'))['total'] or 0

    pedidos_total = Transaccion.objects.count()

    clientes_total = Usuarios.objects.filter(
        Roles__nombre__iexact='cliente').count()

    promedio_venta = Transaccion.objects.aggregate(
        prom=Avg('importe_total'))['prom'] or 0

    transacciones_recientes = (
        Transaccion.objects
        .select_related('solicitud__Usuarios')
        .order_by('-fecha')[:5]
    )

    hoy = timezone.now()
    ventas_mensuales  = []
    pedidos_mensuales = []

    for i in range(5, -1, -1):
        fecha      = hoy - timedelta(days=30 * i)
        mes_inicio = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        siguiente  = fecha.replace(day=28) + timedelta(days=4)
        mes_fin    = siguiente.replace(day=1) if i != 0 else hoy

        total = Transaccion.objects.filter(
            fecha__gte=mes_inicio, fecha__lt=mes_fin
        ).aggregate(total=Sum('importe_total'))['total'] or 0

        count = Transaccion.objects.filter(
            fecha__gte=mes_inicio, fecha__lt=mes_fin
        ).count()

        ventas_mensuales.append({'mes': fecha.strftime('%b'), 'total': float(total)})
        pedidos_mensuales.append({'mes': fecha.strftime('%b'), 'count': count})

    productos_top = (
        Producto.objects
        .annotate(total_vendido=Sum('Solicitud__cantidad'))
        .order_by('-total_vendido')[:5]
    )

    clientes_top = (
        Usuarios.objects
        .filter(Roles__nombre__iexact='cliente')
        .annotate(
            num_pedidos=Count('solicitud'),
            total_gastado=Sum('solicitud__transaccion__importe_total')
        )
        .order_by('-num_pedidos')[:5]
    )

    context = {
        'usuario':                 usuario,
        'ventas_totales':          ventas_totales,
        'pedidos_total':           pedidos_total,
        'clientes_total':          clientes_total,
        'promedio_venta':          round(float(promedio_venta), 2),
        'transacciones_recientes': transacciones_recientes,
        'ventas_mensuales_json':   json.dumps(ventas_mensuales),
        'pedidos_mensuales':       pedidos_mensuales,
        'productos_top':           productos_top,
        'clientes_top':            clientes_top,
        'pagina_activa':           'administrador',
    }
    return render(request, 'administrador.html', context)


# ═══════════════════════════════════════════
#  USUARIOS
# ═══════════════════════════════════════════
@login_requerido
def usuarios(request):
    usuario = get_usuario_sesion(request)

    q          = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()

    qs = Usuarios.objects.select_related('Roles').all()

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q)   |
            Q(apellido__icontains=q) |
            Q(correo__icontains=q)   |
            Q(documento__icontains=q)
        )

    if rol_filtro:
        qs = qs.filter(Roles__nombre__iexact=rol_filtro)

    context = {
        'usuario':        usuario,
        'usuarios':       qs,
        'total_usuarios': Usuarios.objects.count(),
        'roles':          Roles.objects.all(),
        'q':              q,
        'rol_filtro':     rol_filtro,
        'pagina_activa':  'usuarios',
    }
    return render(request, 'usuarios.html', context)


# ═══════════════════════════════════════════
#  TRANSACCIONES
# ═══════════════════════════════════════════
@login_requerido
def transacciones(request):
    usuario = get_usuario_sesion(request)

    q = request.GET.get('q', '').strip()

    qs = Transaccion.objects.select_related(
        'solicitud__Usuarios'
    ).order_by('-fecha')

    if q:
        qs = qs.filter(
            Q(id_pedido__icontains=q) |
            Q(solicitud__Usuarios__nombre__icontains=q) |
            Q(solicitud__Usuarios__apellido__icontains=q)
        )

    total_tx = Transaccion.objects.count()

    context = {
        'usuario':       usuario,
        'transacciones': qs,
        'completadas':   total_tx,
        'pendientes':    0,
        'devueltas':     0,
        'total_tx':      total_tx,
        'q':             q,
        'pagina_activa': 'transacciones',
    }
    return render(request, 'transacciones.html', context)


# ═══════════════════════════════════════════
#  PQRS
# ═══════════════════════════════════════════
@login_requerido
def pqrs(request):
    usuario = get_usuario_sesion(request)

    qs = PQRS.objects.select_related('usuario').order_by('-id_pqrs')

    context = {
        'usuario':       usuario,
        'pqrs_list':     qs,
        'total_pqrs':    qs.count(),
        'pendientes':    qs.count(),
        'en_proceso':    0,
        'resueltos':     0,
        'pagina_activa': 'pqrs',
    }
    return render(request, 'pqrs.html', context)


@login_requerido
def pqrs_responder(request, pk):
    from django.shortcuts import get_object_or_404
    if request.method == 'POST':
        pqrs_obj = get_object_or_404(PQRS, pk=pk)
        # pqrs_obj.respuesta = request.POST.get('respuesta', '')
        # pqrs_obj.save()
    return redirect('pqrs')


# ═══════════════════════════════════════════
#  PERFIL
# ═══════════════════════════════════════════
@login_requerido
def administrador_perfil(request):
    usuario = get_usuario_sesion(request)

    if request.method == 'POST':
        usuario.nombre    = request.POST.get('nombre',    usuario.nombre)
        usuario.apellido  = request.POST.get('apellido',  usuario.apellido)
        usuario.correo    = request.POST.get('correo',    usuario.correo)
        usuario.numero    = request.POST.get('numero',    usuario.numero)
        usuario.direccion = request.POST.get('direccion', usuario.direccion)

        nueva = request.POST.get('nueva_contrasena', '').strip()
        if nueva:
            usuario.contrasena = nueva

        usuario.save()
        request.session['usuario_nombre'] = usuario.nombre
        return redirect('administrador_perfil')

    context = {
        'usuario':       usuario,
        'pagina_activa': 'perfil',
    }
    return render(request, 'administrador_perfil.html', context)