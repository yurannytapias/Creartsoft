from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
import mercadopago
from datetime import timedelta
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.core.paginator import Paginator
import os, zipfile, csv, shutil
from io import TextIOWrapper
from django.core.files import File
from .models import Roles, Permisos, Usuarios, Solicitudes, Productos, PQRS, Transacciones, Inventario, Proveedores, Movimiento, RecetaProducto
from django.contrib import messages
import re
import requests
from django.conf import settings
from django.utils.crypto import get_random_string

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PÃGINAS GENERALES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def index(request):
    return render(request, 'index.html')

def inicio(request):
    return render(request, 'inicio.html')

def recuperar_contrasena(request):
    return render(request, 'recuperar_contrasena.html')

#usuario-invitado (sin sesion) cliente-invitado 
def index(request):
    usuario = get_usuario_sesion(request)
    return render(request, 'index.html', {
        'usuario': usuario,
        'es_index': True,  # esta variable
})

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PROTECTORES DE SESIÃ“N
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def login_requerido(vista):
    # Redirige al login si no hay sesiÃ³n activa
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('inicio')
        return vista(request, *args, **kwargs)
    wrapper.__name__ = vista.__name__
    return wrapper


def get_usuario_sesion(request): 
    # Retorna el objeto Usuarios de la sesiÃ³n activa o None
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            return Usuarios.objects.select_related('rol').get(pk=usuario_id)
        except Usuarios.DoesNotExist:
            pass
    return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  AUTENTICACIÃ“N
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def registrar_usuario(request):
    if request.method != "POST":
        return render(request, "inicio.html")

    correo = request.POST.get("correo")
    contrasena = request.POST.get("contrasena")
    nombre = request.POST.get("nombre")
    apellido = request.POST.get("apellido")
    numero = request.POST.get("numero")
    direccion = request.POST.get("direccion", "")

    if not all([nombre, apellido, correo, numero, contrasena]):
        messages.warning(request, "Todos los campos son obligatorios.")
        return redirect("inicio")

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
        messages.error(request, "El correo no es vÃ¡lido.")
        return redirect("inicio")

    if Usuarios.objects.filter(correo=correo).exists():
        messages.error(request, "Este correo ya estÃ¡ registrado.")
        return redirect("inicio")

    try:
        rol_cliente = Roles.objects.get(nombre="cliente")

        token = get_random_string(64)

        usuario = Usuarios.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            numero=numero,
            direccion=direccion,
            contrasena=make_password(contrasena),
            rol=rol_cliente,
            estado=False,
            token_activacion=token
        )

        correo_activacion(usuario, request)

        messages.success(
            request,
            "Cuenta creada. Revisa tu correo para activar la cuenta."
        )

        return redirect("inicio")

    except Exception as e:
        print(e)
        messages.error(
            request,
            "OcurriÃ³ un error al crear la cuenta."
        )
        return redirect("inicio")

def login_usuario(request):
    if request.method != "POST":
        return render(request, "inicio.html")
    
    correo     = request.POST.get("correo", "").strip()
    contrasena = request.POST.get("contrasena", "").strip()

    if not correo or not contrasena:
        messages.warning(request, "Por favor, completa todos los campos obligatorios.")
        return redirect("inicio")

    try:
        usuario = Usuarios.objects.get(correo=correo)

        if not check_password(contrasena, usuario.contrasena):
            messages.error(request, "La contraseÃ±a es incorrecta. Por favor, intÃ©ntalo de nuevo.")
            return redirect("inicio")

        # Verificar si la cuenta estÃ¡ activada
        if not usuario.estado:
            messages.error(
                request,
                "Debes activar tu cuenta desde el correo electrÃ³nico antes de iniciar sesiÃ³n."
            )
            return redirect("inicio")

        request.session['usuario_id'] = usuario.id_usuario
        request.session['usuario_nombre'] = usuario.nombre

        messages.success(
            request,
            "Â¡Bienvenido/a de nuevo! Has iniciado sesiÃ³n correctamente."
        )

        rol = usuario.rol.nombre

        if rol == "administrador":
            return redirect("administrador")

        if rol == "vendedor":
            return redirect("vendedor")

        if rol == "cliente":
            return redirect("catalogo")

        return redirect("index")

    except Usuarios.DoesNotExist:
        messages.error(
            request,
            "No existe una cuenta con ese correo electrÃ³nico."
        )
        return redirect("inicio")


def cerrar_sesion(request):
    request.session.flush()
    messages.success(request, "Has cerrado sesiÃ³n correctamente. Â¡Hasta pronto!")
    return redirect("inicio")



# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  ADMINISTRADOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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
        .select_related('solicitud__usuario', 'solicitud__producto')
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
        'pedidos_mensuales_json': json.dumps(pedidos_mensuales),
        'pedidos_mensuales': pedidos_mensuales,
        'productos_top': productos_top,
        'clientes_top': clientes_top,
        'pagina_activa': 'administrador',
    }
    return render(request, 'administrador/administrador.html', context)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  USUARIOS (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def usuarios(request):
    usuario = get_usuario_sesion(request)

    # â”€â”€ REGISTRAR USUARIO â”€â”€
    if request.method == 'POST' and request.POST.get('accion') == 'registrar_usuario':
        nombre     = request.POST.get('nombre', '').strip()
        apellido   = request.POST.get('apellido', '').strip()
        correo     = request.POST.get('correo', '').strip().lower()
        numero     = request.POST.get('numero', '').strip()
        direccion  = request.POST.get('direccion', '').strip()
        contrasena = request.POST.get('contrasena', '')
        rol_nombre = request.POST.get('rol', '').strip()

        if not all([nombre, apellido, correo, numero, contrasena, rol_nombre]):
            messages.warning(request, "Todos los campos son obligatorios.")
            return redirect('usuarios')

        if Usuarios.objects.filter(correo=correo).exists():
            messages.error(request, f"El correo {correo} ya estÃ¡ registrado.")
            return redirect('usuarios')

        try:
            rol_obj = Roles.objects.get(nombre=rol_nombre)
            Usuarios.objects.create(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                numero=numero,
                direccion=direccion or None,
                contrasena=make_password(contrasena),
                rol=rol_obj,
                estado=True,
            )
            messages.success(request, f"Usuario {nombre} {apellido} registrado exitosamente.")
        except Roles.DoesNotExist:
            messages.error(request, f"El rol '{rol_nombre}' no existe en la base de datos.")
        except Exception:
            messages.error(request, "OcurriÃ³ un error al registrar el usuario. Intenta de nuevo.")

        return redirect('usuarios')

    # â”€â”€ TOGGLE ESTADO â”€â”€
    if request.method == 'POST' and request.POST.get('accion') == 'toggle_estado':
        uid = request.POST.get('usuario_id')
        try:
            u = Usuarios.objects.get(pk=uid)
            u.estado = not u.estado
            u.save()
            estado_txt = "activado" if u.estado else "desactivado"
            messages.success(request, f"Usuario {u.nombre} {u.apellido} {estado_txt} correctamente.")
        except Usuarios.DoesNotExist:
            messages.error(request, "No se encontrÃ³ el usuario.")
        return redirect('usuarios')

    # â”€â”€ LISTADO â”€â”€
    q = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()

    qs = Usuarios.objects.select_related('rol').all()
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) |
            Q(correo__icontains=q) | Q(numero__icontains=q)
        )
    if rol_filtro:
        qs = qs.filter(rol__nombre__iexact=rol_filtro)

    context = {
        'usuario':          usuario,
        'usuarios':         qs,
        'roles':            Roles.objects.all(),
        'total_usuarios':   Usuarios.objects.count(),
        'total_activos':    Usuarios.objects.filter(estado=True).count(),
        'total_clientes':   Usuarios.objects.filter(rol__nombre__iexact='cliente').count(),
        'total_vendedores': Usuarios.objects.filter(rol__nombre__iexact='vendedor').count(),
        'q':                q,
        'rol_filtro':       rol_filtro,
        'pagina_activa':    'usuarios',
    }
    return render(request, 'administrador/usuarios.html', context)



#reportes usuarios 
@login_requerido
def usuarios_export_excel(request):
    q          = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()
 
    qs = Usuarios.objects.select_related('rol').all()
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) |
            Q(correo__icontains=q) | Q(numero__icontains=q)
        )
    if rol_filtro:
        qs = qs.filter(rol__nombre__iexact=rol_filtro)
    
    if not qs.exists():
        messages.warning(request, "No hay usuarios para exportar.")
        return redirect('usuarios')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Usuarios"
 
    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")
 
    headers = ["ID", "Nombre", "Apellido", "Correo", "NÃºmero", "Rol", "Estado", "Fecha registro"]
    ws.append(headers)
    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig
 
    for u in qs:
        ws.append([
            u.id_usuario,
            u.nombre,
            u.apellido,
            u.correo,
            u.numero,
            u.rol.nombre if u.rol else '',
            'Activo' if u.estado else 'Inactivo',
            u.fecha_creacion.strftime("%Y-%m-%d"),
        ])
 
    anchos = [8, 20, 20, 30, 16, 14, 10, 16]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho
 
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="usuarios.xlsx"'
    wb.save(response)
    return response
 
 
@login_requerido
def usuarios_export_pdf(request):
    q          = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()
 
    qs = Usuarios.objects.select_related('rol').all()
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) |
            Q(correo__icontains=q) | Q(numero__icontains=q)
        )
    if rol_filtro:
        qs = qs.filter(rol__nombre__iexact=rol_filtro)
    
    if not qs.exists():
        messages.warning(request, "No hay usuarios para exportar.")
        return redirect('usuarios')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="usuarios.pdf"'
 
    doc      = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = [Paragraph("<b>Reporte de Usuarios</b>", styles['Title']), Spacer(1, 12)]
 
    data = [["ID", "Nombre", "Apellido", "Correo", "NÃºmero", "Rol", "Estado", "Fecha"]]
    for u in qs:
        data.append([str(u.id_usuario), u.nombre, u.apellido, u.correo, u.numero,
                     u.rol.nombre if u.rol else '', 'Activo' if u.estado else 'Inactivo',
                     u.fecha_creacion.strftime("%Y-%m-%d")])
 
    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    doc.build(elements)
    return response

@login_requerido
def crm_export_excel(request):
    from django.db.models import Count, Sum, Q

    clientes_qs = Usuarios.objects.filter(rol__nombre__iexact='cliente')

    clientes_data = (
        clientes_qs
        .annotate(
            total_pedidos=Count('solicitudes'),
            ltv=Sum(
                'solicitudes__precio_total',
                filter=Q(solicitudes__estado='pagada')
            )
        )
        .values('id_usuario', 'nombre', 'apellido', 'total_pedidos', 'ltv')
        .order_by('-ltv')
    )

    wb = openpyxl.Workbook()

    # â”€â”€ Hoja 1: Nuevos vs Recurrentes â”€â”€
    ws1 = wb.active
    ws1.title = "Nuevos vs Recurrentes"

    header_fill = PatternFill("solid", fgColor="612D53")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")

    ws1.append(["Reporte: Clientes Nuevos vs Recurrentes"])
    ws1['A1'].font = Font(bold=True, size=13, color="612D53")
    ws1.append([])

    total = clientes_qs.count()
    recurrentes = [c for c in clientes_data if c['total_pedidos'] > 1]
    nuevos      = [c for c in clientes_data if c['total_pedidos'] <= 1]
    tasa = round(len(recurrentes) / total * 100, 1) if total else 0

    resumen_headers = ["Total clientes", "Clientes nuevos", "Clientes recurrentes", "Tasa de retenciÃ³n (%)"]
    ws1.append(resumen_headers)
    for col_num in range(1, 5):
        cell = ws1.cell(row=3, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    ws1.append([total, len(nuevos), len(recurrentes), tasa])
    ws1.append([])

    detalle_headers = ["ID", "Nombre", "Apellido", "Total pedidos", "Tipo"]
    ws1.append(detalle_headers)
    for col_num in range(1, 6):
        cell = ws1.cell(row=6, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    for c in clientes_data:
        tipo = "Recurrente" if c['total_pedidos'] > 1 else "Nuevo"
        ws1.append([c['id_usuario'], c['nombre'], c['apellido'], c['total_pedidos'], tipo])

    for i, ancho in enumerate([8, 20, 20, 16, 14], 1):
        ws1.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    # â”€â”€ Hoja 2: LTV Clientes â”€â”€
    ws2 = wb.create_sheet(title="LTV Clientes")

    ws2.append(["Reporte: Valor de Vida del Cliente (LTV)"])
    ws2['A1'].font = Font(bold=True, size=13, color="612D53")
    ws2.append([])

    ltv_headers = ["#", "ID", "Nombre", "Apellido", "Total pedidos", "Tipo", "LTV acumulado ($)"]
    ws2.append(ltv_headers)
    for col_num in range(1, 8):
        cell = ws2.cell(row=3, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    for idx, c in enumerate(clientes_data, 1):
        tipo = "Recurrente" if c['total_pedidos'] > 1 else "Nuevo"
        ltv_val = c['ltv'] or 0
        ws2.append([idx, c['id_usuario'], c['nombre'], c['apellido'],
                    c['total_pedidos'], tipo, round(ltv_val, 2)])

    for i, ancho in enumerate([6, 8, 20, 20, 16, 14, 20], 1):
        ws2.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_crm.xlsx"'
    wb.save(response)
    return response


@login_requerido
def crm_export_pdf(request):
    from django.db.models import Count, Sum, Q

    clientes_qs = Usuarios.objects.filter(rol__nombre__iexact='cliente')

    clientes_data = list(
        clientes_qs
        .annotate(
            total_pedidos=Count('solicitudes'),
            ltv=Sum(
                'solicitudes__precio_total',
                filter=Q(solicitudes__estado='pagada')
            )
        )
        .values('id_usuario', 'nombre', 'apellido', 'total_pedidos', 'ltv')
        .order_by('-ltv')
    )

    total = clientes_qs.count()
    recurrentes = [c for c in clientes_data if c['total_pedidos'] > 1]
    nuevos      = [c for c in clientes_data if c['total_pedidos'] <= 1]
    tasa = round(len(recurrentes) / total * 100, 1) if total else 0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_crm.pdf"'

    doc      = SimpleDocTemplate(response, pagesize=landscape(A4),
                                  leftMargin=20, rightMargin=20,
                                  topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = []

    COLOR_HEADER = colors.HexColor('#612D53')
    COLOR_ALT    = colors.HexColor('#fdf5f5')

    style_tabla = TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0), COLOR_HEADER),
        ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
        ('FONTNAME',       (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, 0), 9),
        ('ALIGN',          (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',         (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE',       (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_ALT]),
        ('GRID',           (0, 0), (-1, -1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0, 0), (-1, -1), 20),
    ])

    # â”€â”€ SecciÃ³n 1: Resumen nuevos vs recurrentes â”€â”€
    elements.append(Paragraph("<b>Reporte CRM â€” Clientes Nuevos vs Recurrentes</b>", styles['Title']))
    elements.append(Spacer(1, 8))

    resumen_data = [
        ["Total clientes", "Clientes nuevos", "Clientes recurrentes", "Tasa de retenciÃ³n"],
        [str(total), str(len(nuevos)), str(len(recurrentes)), f"{tasa}%"],
    ]
    t_resumen = Table(resumen_data, colWidths=[130, 130, 130, 130])
    t_resumen.setStyle(style_tabla)
    elements.append(t_resumen)
    elements.append(Spacer(1, 14))

    detalle_data = [["ID", "Nombre", "Apellido", "Pedidos", "Tipo"]]
    for c in clientes_data:
        tipo = "Recurrente" if c['total_pedidos'] > 1 else "Nuevo"
        detalle_data.append([
            str(c['id_usuario']), c['nombre'], c['apellido'],
            str(c['total_pedidos']), tipo,
        ])
    t_detalle = Table(detalle_data, repeatRows=1)
    t_detalle.setStyle(style_tabla)
    elements.append(t_detalle)

    # â”€â”€ SecciÃ³n 2: LTV â”€â”€
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Reporte CRM â€” Valor de Vida del Cliente (LTV)</b>", styles['Title']))
    elements.append(Spacer(1, 8))

    ltv_data = [["#", "ID", "Nombre", "Apellido", "Pedidos", "Tipo", "LTV ($)"]]
    for idx, c in enumerate(clientes_data, 1):
        tipo    = "Recurrente" if c['total_pedidos'] > 1 else "Nuevo"
        ltv_val = c['ltv'] or 0
        ltv_data.append([
            str(idx), str(c['id_usuario']), c['nombre'], c['apellido'],
            str(c['total_pedidos']), tipo,
            f"${ltv_val:,.0f}",
        ])
    t_ltv = Table(ltv_data, repeatRows=1)
    t_ltv.setStyle(style_tabla)
    elements.append(t_ltv)

    doc.build(elements)
    return response

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  TRANSACCIONES (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 
def _filtrar_transacciones(request):
    """Helper sin decorador."""
    q           = request.GET.get('q', '').strip()
    estado      = request.GET.get('estado', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '').strip()
    fecha_hasta = request.GET.get('fecha_hasta', '').strip()
 
    qs = Transacciones.objects.select_related(
        'solicitud__usuario', 'solicitud__producto'
    ).order_by('-fecha_creacion')
 
    if q:
        qs = qs.filter(
            Q(id_transaccion__icontains=q) |
            Q(solicitud__usuario__nombre__icontains=q) |
            Q(solicitud__usuario__apellido__icontains=q) |
            Q(solicitud__producto__nombre__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    if fecha_desde:
        qs = qs.filter(fecha_creacion__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_creacion__date__lte=fecha_hasta)
 
    return qs
 
 
@login_requerido
def transacciones(request):
    usuario = get_usuario_sesion(request)
    qs      = _filtrar_transacciones(request)
 
    context = {
        'usuario':       usuario,
        'transacciones': qs,
        'completadas':   qs.filter(estado='terminado').count(),
        'abonadas':      qs.filter(estado='abonado').count(),
        'total_tx':      qs.count(),
        'q':             request.GET.get('q', ''),
        'f_estado':      request.GET.get('estado', ''),
        'f_desde':       request.GET.get('fecha_desde', ''),
        'f_hasta':       request.GET.get('fecha_hasta', ''),
        'pagina_activa': 'transacciones',
    }
    return render(request, 'administrador/transacciones.html', context)
 
 
@login_requerido
def transacciones_export_excel(request):
    qs = _filtrar_transacciones(request)
    
    if not qs.exists():
        messages.warning(request, "No hay transacciones para exportar.")
        return redirect('transacciones')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transacciones"
 
    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")
 
    headers = ["ID", "Cliente", "Producto", "Importe", "Moneda", "MÃ©todo pago", "Estado", "Fecha"]
    ws.append(headers)
    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig
 
    for t in qs:
        if t.solicitud:
            cliente  = f"{t.solicitud.usuario.nombre} {t.solicitud.usuario.apellido}" if t.solicitud.usuario else t.solicitud.nombre_invitado or 'Invitado'
            producto = t.solicitud.producto.nombre
        else:
            cliente = producto = ''
        ws.append([f"#{t.id_transaccion}", cliente, producto, float(t.importe_total),
                   t.moneda, t.metodo_pago, t.estado, t.fecha_creacion.strftime("%Y-%m-%d")])
 
    anchos = [10, 25, 25, 14, 10, 18, 12, 14]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho
 
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transacciones.xlsx"'
    wb.save(response)
    return response
 
 
@login_requerido
def transacciones_export_pdf(request):
    qs = _filtrar_transacciones(request)
    
    if not qs.exists():
        messages.warning(request, "No hay transacciones para exportar.")
        return redirect('transacciones')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transacciones.pdf"'
 
    doc      = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = [Paragraph("<b>Reporte de Transacciones</b>", styles['Title']), Spacer(1, 12)]
 
    data = [["ID", "Cliente", "Producto", "Importe", "MÃ©todo pago", "Estado", "Fecha"]]
    for t in qs:
        if t.solicitud:
            cliente  = f"{t.solicitud.usuario.nombre} {t.solicitud.usuario.apellido}" if t.solicitud.usuario else t.solicitud.nombre_invitado or 'Invitado'
            producto = t.solicitud.producto.nombre
        else:
            cliente = producto = ''
        data.append([f"#{t.id_transaccion}", cliente, producto, f"${t.importe_total}",
                     t.metodo_pago, t.estado.capitalize(), t.fecha_creacion.strftime("%Y-%m-%d")])
 
    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    doc.build(elements)
    return response
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PRODUCTOS (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def productos(request):
    usuario = get_usuario_sesion(request)

    qs = _filtrar_productos(request)

    # Excluir productos de eventos pendientes SIN receta
    # (diarios y antojos pasan siempre, no importa si tienen receta)
    qs = qs.exclude(
        categoria='eventos',
        estado_aprobacion='pendiente',
        receta__isnull=True
    )

    pendientes = Productos.objects.filter(estado_aprobacion='pendiente').count()
    aprobados  = Productos.objects.filter(estado_aprobacion='aprobado').count()
    rechazados = Productos.objects.filter(estado_aprobacion='rechazado').count()
    inactivos  = Productos.objects.filter(estado=False).order_by('-fecha_creacion')
    total_tx   = Productos.objects.count()

    # â”€â”€ datos reporte â”€â”€
    productos_ranking = (
        Productos.objects
        .filter(estado_aprobacion='aprobado')
        .annotate(
            total_solicitudes=Count('solicitudes__id_solicitud'),
            solicitudes_pagadas=Count(
                'solicitudes__id_solicitud',
                filter=Q(solicitudes__estado='pagada')
            ),
            ingresos_generados=Sum(
                'solicitudes__precio_total',
                filter=Q(solicitudes__estado='pagada')
            ),
        )
        .order_by('-solicitudes_pagadas', '-total_solicitudes')[:20]
    )

    ingresos_totales = (
        Solicitudes.objects
        .filter(estado='pagada')
        .aggregate(t=Sum('precio_total'))['t'] or 0
    )
    total_pagadas = Solicitudes.objects.filter(estado='pagada').count()
    top1          = productos_ranking.first()

    top10         = list(productos_ranking[:10])
    chart_labels  = json.dumps([p.nombre for p in top10])
    chart_valores = json.dumps([p.solicitudes_pagadas for p in top10])

    context = {
        'usuario': usuario,
        'inactivos': inactivos,
        'productos': qs,
        'pendientes': pendientes,
        'aprobados': aprobados,
        'rechazados': rechazados,
        'total_tx': total_tx,
        'q': request.GET.get('q', ''),
         # reporte
        'productos_ranking': productos_ranking,
        'ingresos_totales':  ingresos_totales,
        'total_pagadas':     total_pagadas,
        'top1':              top1,
        'chart_labels':      chart_labels,
        'chart_valores':     chart_valores,
    }
    return render(request, 'administrador/productos.html', context)

#acciones ------------------------------------------------------------------------------>
#acciones ------------------------------------------------------------------------------>

@login_requerido
def cambiar_estado_producto(request, id_producto):
    if request.method == "POST":
        try:
            producto = Productos.objects.get(id_producto=id_producto)
            accion = request.POST.get("accion")

            if accion == "aprobar":
                producto.estado_aprobacion = "aprobado"
                messages.success(request, "Producto aceptado.")

            elif accion == "rechazar":
                producto.estado_aprobacion = "rechazado"
                producto.motivo_rechazo = request.POST.get("motivo", "")
                messages.info(request, "Producto rechazado.")

            producto.save()
        except Exception as e:
            messages.error(request, "OcurriÃ³ un error al cambiar el estado del producto. Intentelo de nuevo.")

    return redirect("productos")

def _filtrar_productos(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()

    qs = Productos.objects.select_related('vendedor').order_by('-id_producto')

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(vendedor__nombre__icontains=q) |
            Q(vendedor__apellido__icontains=q)
        )
    if estado:
        qs = qs.filter(estado_aprobacion=estado)

    return qs


@login_requerido
def productos_export_excel(request):
    qs = _filtrar_productos(request)

    if not qs.exists():
        messages.warning(request, "No hay productos para exportar.")
        return redirect('productos')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")

    headers = ["ID", "Nombre", "Descripcion", "Precio", "Categoria", "Estado", "Motivo Rechazo", "Vendedor"]
    ws.append(headers)
    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    for p in qs:
        vendedor = f"{p.vendedor.nombre} {p.vendedor.apellido}" if p.vendedor else ''
        ws.append([
            f"#{p.id_producto}",
            p.nombre,
            p.descripcion,
            f"${p.precio}",
            p.categoria,
            p.estado_aprobacion.capitalize(),
            p.motivo_rechazo or '',
            vendedor
        ])

    anchos = [10, 25, 35, 12, 12, 12, 30, 25]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="productos.xlsx"'
    wb.save(response)
    return response


@login_requerido
def productos_export_pdf(request):
    qs = _filtrar_productos(request)

    if not qs.exists():
        messages.warning(request, "No hay productos para exportar.")
        return redirect('productos')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="productos.pdf"'

    doc      = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = [Paragraph("<b>Reporte de Productos</b>", styles['Title']), Spacer(1, 12)]

    data = [["ID", "Nombre", "Descripcion", "Precio", "Categoria", "Estado", "Vendedor"]]
    for p in qs:
        vendedor = f"{p.vendedor.nombre} {p.vendedor.apellido}" if p.vendedor else ''
        data.append([
            f"#{p.id_producto}",
            p.nombre,
            p.descripcion,
            f"${p.precio}",
            p.categoria,
            p.estado_aprobacion.capitalize(),
            vendedor
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    doc.build(elements)
    return response
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  REPORTE: PRODUCTOS MÃS VENDIDOS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@login_requerido
def reporte_productos_mas_vendidos(request):
    usuario = get_usuario_sesion(request)

    # â”€â”€ ranking: solo productos aprobados con al menos 1 solicitud pagada â”€â”€
    productos_ranking = (
        Productos.objects
        .filter(estado_aprobacion='aprobado')
        .annotate(
            total_solicitudes=Count('solicitudes__id_solicitud'),
            solicitudes_pagadas=Count(
                'solicitudes__id_solicitud',
                filter=Q(solicitudes__estado='pagada')
            ),
            ingresos_generados=Sum(
                'solicitudes__precio_total',
                filter=Q(solicitudes__estado='pagada')
            ),
        )
        .order_by('-solicitudes_pagadas', '-total_solicitudes')[:20]
    )

    # â”€â”€ tarjetas resumen â”€â”€
    total_productos   = Productos.objects.filter(estado_aprobacion='aprobado').count()
    total_solicitudes = Solicitudes.objects.count()
    total_pagadas     = Solicitudes.objects.filter(estado='pagada').count()
    ingresos_totales  = (
        Solicitudes.objects
        .filter(estado='pagada')
        .aggregate(t=Sum('precio_total'))['t'] or 0
    )

    # â”€â”€ top 1 para destacar â”€â”€
    top1 = productos_ranking.first()

    # â”€â”€ JSON para Chart.js â”€â”€
    import json
    top10 = list(productos_ranking[:10])
    chart_labels  = [p.nombre for p in top10]
    chart_valores = [p.solicitudes_pagadas for p in top10]

    context = {
        'usuario':             usuario,
        'pagina_activa':       'productos',
        'productos_ranking':   productos_ranking,
        'total_productos':     total_productos,
        'total_solicitudes':   total_solicitudes,
        'total_pagadas':       total_pagadas,
        'ingresos_totales':    ingresos_totales,
        'top1':                top1,
        'chart_labels':        json.dumps(chart_labels),
        'chart_valores':       json.dumps(chart_valores),
    }
    return render(request, 'administrador/reporte_productos_mas_vendidos.html', context)

@login_requerido
def reporte_productos_pdf(request):
    from reportlab.platypus import HRFlowable
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from datetime import date

    productos_ranking = (
        Productos.objects
        .filter(estado_aprobacion='aprobado')
        .annotate(
            total_solicitudes=Count('solicitudes__id_solicitud'),
            solicitudes_pagadas=Count(
                'solicitudes__id_solicitud',
                filter=Q(solicitudes__estado='pagada')
            ),
            ingresos_generados=Sum(
                'solicitudes__precio_total',
                filter=Q(solicitudes__estado='pagada')
            ),
        )
        .order_by('-solicitudes_pagadas', '-total_solicitudes')[:20]
    )

    ingresos_totales = (
        Solicitudes.objects
        .filter(estado='pagada')
        .aggregate(t=Sum('precio_total'))['t'] or 0
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_productos_mas_vendidos.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    VINO   = colors.HexColor('#7a2d3e')
    VINO_L = colors.HexColor('#fdf5f5')
    thin   = colors.HexColor('#e0c8c8')
    styles = getSampleStyleSheet()
    elements = []

    titulo_style = ParagraphStyle('t', fontSize=18, textColor=VINO,
                                  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    sub_style    = ParagraphStyle('s', fontSize=10, textColor=colors.HexColor('#888888'),
                                  alignment=TA_CENTER, spaceAfter=16)
    sec_style    = ParagraphStyle('sc', fontSize=12, textColor=colors.HexColor('#2a1010'),
                                  fontName='Helvetica-Bold', spaceAfter=10)

    elements.append(Paragraph("CreartSoft â€” Productos MÃ¡s Vendidos", titulo_style))
    elements.append(Paragraph(f"Generado el {date.today().strftime('%d/%m/%Y')}", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=VINO, spaceAfter=20))

    # â”€â”€ tarjetas â”€â”€
    total_productos = Productos.objects.filter(estado_aprobacion='aprobado').count()
    total_pagadas   = Solicitudes.objects.filter(estado='pagada').count()

    card_data = [[
        Paragraph(f"<b>{total_productos}</b><br/>Productos activos", styles['Normal']),
        Paragraph(f"<b>{total_pagadas}</b><br/>Ventas pagadas",      styles['Normal']),
        Paragraph(f"<b>${ingresos_totales:,.0f}</b><br/>Ingresos totales", styles['Normal']),
    ]]
    card_table = Table(card_data, colWidths=[5*cm, 4*cm, 5*cm])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#EDE9FE')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#D1FAE5')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#DBEAFE')),
        ('ALIGN',   (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',  (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',(0,0), (-1,-1), 11),
        ('FONTNAME',(0,0), (-1,-1), 'Helvetica-Bold'),
        ('ROWHEIGHT',(0,0),(-1,-1), 44),
        ('BOX',     (0,0), (-1,-1), 0, colors.white),
        ('INNERGRID',(0,0),(-1,-1), 3, colors.white),
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 20))

    # â”€â”€ ranking â”€â”€
    elements.append(HRFlowable(width="100%", thickness=0.5, color=thin, spaceAfter=10))
    elements.append(Paragraph("Ranking de productos mÃ¡s vendidos (top 20)", sec_style))

    data = [['#', 'Producto', 'CategorÃ­a', 'Vendedor', 'Solicitudes', 'Pagadas', 'Ingresos ($)']]
    for i, p in enumerate(productos_ranking, 1):
        vendedor = f"{p.vendedor.nombre} {p.vendedor.apellido}" if p.vendedor else 'â€”'
        data.append([
            str(i),
            p.nombre,
            p.get_categoria_display(),
            vendedor,
            str(p.total_solicitudes),
            str(p.solicitudes_pagadas),
            f"${p.ingresos_generados:,.0f}" if p.ingresos_generados else '$0',
        ])

    tabla = Table(data, colWidths=[1*cm, 4*cm, 2.5*cm, 3.5*cm, 2*cm, 2*cm, 2.5*cm],
                  repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), VINO),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, VINO_L]),
        # destacar top 3
        ('FONTNAME',       (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTNAME',       (0,2), (-1,2), 'Helvetica-Bold'),
        ('FONTNAME',       (0,3), (-1,3), 'Helvetica-Bold'),
        ('BACKGROUND',     (0,1), (-1,1), colors.HexColor('#FEF3C7')),
        ('BACKGROUND',     (0,2), (-1,2), colors.HexColor('#F3F4F6')),
        ('BACKGROUND',     (0,3), (-1,3), colors.HexColor('#FEF3C7')),
        ('GRID',           (0,0), (-1,-1), 0.4, thin),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 16))

    elements.append(HRFlowable(width="100%", thickness=1, color=VINO, spaceBefore=6, spaceAfter=6))
    pie_style = ParagraphStyle('pie', fontSize=8, textColor=colors.HexColor('#aaaaaa'),
                                alignment=TA_CENTER)
    elements.append(Paragraph("CreartSoft Â· Reporte generado automÃ¡ticamente", pie_style))

    doc.build(elements)
    return response


@login_requerido
def reporte_productos_excel(request):
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Border, Side
    from openpyxl.chart import BarChart, Reference
    from datetime import date

    productos_ranking = (
        Productos.objects
        .filter(estado_aprobacion='aprobado')
        .annotate(
            total_solicitudes=Count('solicitudes__id_solicitud'),
            solicitudes_pagadas=Count(
                'solicitudes__id_solicitud',
                filter=Q(solicitudes__estado='pagada')
            ),
            ingresos_generados=Sum(
                'solicitudes__precio_total',
                filter=Q(solicitudes__estado='pagada')
            ),
        )
        .order_by('-solicitudes_pagadas', '-total_solicitudes')[:20]
    )

    ingresos_totales = (
        Solicitudes.objects
        .filter(estado='pagada')
        .aggregate(t=Sum('precio_total'))['t'] or 0
    )
    total_productos = Productos.objects.filter(estado_aprobacion='aprobado').count()
    total_pagadas   = Solicitudes.objects.filter(estado='pagada').count()

    wb  = openpyxl.Workbook()
    ws  = wb.active
    ws.title = "Productos mÃ¡s vendidos"
    ws.sheet_view.showGridLines = False

    VINO   = "7a2d3e"
    VINO_L = "fdf5f5"
    BLANCO = "FFFFFF"
    h_font = Font(name='Calibri', bold=True, color=BLANCO, size=11)
    h_fill = PatternFill("solid", fgColor=VINO)
    h_alig = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin   = Side(style='thin', color='e0c8c8')
    borde  = Border(left=thin, right=thin, top=thin, bottom=thin)

    # â”€â”€ tÃ­tulo â”€â”€
    ws.merge_cells('A1:G1')
    ws['A1'] = 'CreartSoft â€” Productos MÃ¡s Vendidos'
    ws['A1'].font = Font(name='Calibri', bold=True, size=15, color=VINO)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 34

    ws.merge_cells('A2:G2')
    ws['A2'] = f'Generado el {date.today().strftime("%d/%m/%Y")}'
    ws['A2'].font = Font(name='Calibri', size=10, color='888888')
    ws['A2'].alignment = Alignment(horizontal='center')
    ws.row_dimensions[2].height = 16

    # â”€â”€ tarjetas fila 4-6 â”€â”€
    tarjetas = [
        ('Productos activos', str(total_productos),        'EDE9FE', '5B21B6'),
        ('Ventas pagadas',    str(total_pagadas),           'D1FAE5', '065F46'),
        ('Ingresos totales',  f"${ingresos_totales:,.0f}", 'DBEAFE', '1E3A8A'),
    ]
    ws.row_dimensions[4].height = 12
    ws.row_dimensions[5].height = 28
    ws.row_dimensions[6].height = 16
    ws.row_dimensions[7].height = 12

    for ci, (label, valor, bg, fg) in enumerate(tarjetas, 1):
        c_v = ws.cell(row=5, column=ci, value=valor)
        c_v.font = Font(name='Calibri', bold=True, size=13, color=fg)
        c_v.fill = PatternFill("solid", fgColor=bg)
        c_v.alignment = Alignment(horizontal='center', vertical='center')
        c_v.border = borde
        c_l = ws.cell(row=6, column=ci, value=label)
        c_l.font = Font(name='Calibri', size=9, color=fg)
        c_l.fill = PatternFill("solid", fgColor=bg)
        c_l.alignment = Alignment(horizontal='center', vertical='center')
        c_l.border = borde

    # â”€â”€ tabla ranking (fila 9) â”€â”€
    ws.row_dimensions[9].height = 20
    headers = ['#', 'Producto', 'CategorÃ­a', 'Vendedor', 'Total solicitudes', 'Ventas pagadas', 'Ingresos ($)']
    for ci, h in enumerate(headers, 1):
        c = ws.cell(row=9, column=ci, value=h)
        c.font = h_font; c.fill = h_fill
        c.alignment = h_alig; c.border = borde

    medallas = {1: 'FEF08A', 2: 'E5E7EB', 3: 'FED7AA'}  # oro, plata, bronce

    for ri, p in enumerate(productos_ranking, 10):
        pos = ri - 9
        ws.row_dimensions[ri].height = 18
        vendedor = f"{p.vendedor.nombre} {p.vendedor.apellido}" if p.vendedor else 'â€”'
        bg = medallas.get(pos, VINO_L if ri % 2 == 0 else BLANCO)
        fila = [
            pos,
            p.nombre,
            p.get_categoria_display(),
            vendedor,
            p.total_solicitudes,
            p.solicitudes_pagadas,
            float(p.ingresos_generados or 0),
        ]
        for ci, valor in enumerate(fila, 1):
            c = ws.cell(row=ri, column=ci, value=valor)
            c.fill = PatternFill("solid", fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')
            c.border = borde
            c.font = Font(name='Calibri', size=10,
                          bold=(pos <= 3))
            if ci == 7:
                c.number_format = '$#,##0.00'

    # â”€â”€ grÃ¡fica de barras (top 10) â”€â”€
    last_row = 9 + min(len(list(productos_ranking)), 10)
    chart = BarChart()
    chart.type    = "col"
    chart.style   = 10
    chart.title   = "Top 10 productos mÃ¡s vendidos"
    chart.y_axis.title = "Ventas pagadas"
    chart.x_axis.title = "Producto"
    chart.grouping = "clustered"

    data_ref   = Reference(ws, min_col=6, min_row=9, max_row=last_row)
    labels_ref = Reference(ws, min_col=2, min_row=10, max_row=last_row)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(labels_ref)
    chart.series[0].graphicalProperties.solidFill = "7a2d3e"
    chart.width  = 16
    chart.height = 12
    ws.add_chart(chart, "I9")

    # â”€â”€ anchos columnas â”€â”€
    for col, ancho in zip(range(1, 8), [5, 28, 14, 22, 16, 14, 16]):
        ws.column_dimensions[get_column_letter(col)].width = ancho

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_productos_mas_vendidos.xlsx"'
    wb.save(response)
    return response

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  SOLICITUDES (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def _filtrar_solicitudes(request):
    qs = Solicitudes.objects.select_related(
        'usuario', 'producto__vendedor'
    ).filter(
        producto__categoria='eventos' 
    ).order_by('-fecha_creacion')

    q          = request.GET.get('q', '').strip()
    estado     = request.GET.get('estado', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '').strip()
    fecha_hasta = request.GET.get('fecha_hasta', '').strip()
    precio_min  = request.GET.get('precio_min', '').strip()
    precio_max  = request.GET.get('precio_max', '').strip()
    categoria   = request.GET.get('categoria', '').strip()

    if q:
        qs = qs.filter(
            Q(id_solicitud__icontains=q) |
            Q(usuario__nombre__icontains=q) |
            Q(usuario__apellido__icontains=q) |
            Q(producto__nombre__icontains=q) |
            Q(nombre_invitado__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    if fecha_desde:
        qs = qs.filter(fecha_creacion__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_creacion__date__lte=fecha_hasta)
    if precio_min:
        qs = qs.filter(precio_total__gte=precio_min)
    if precio_max:
        qs = qs.filter(precio_total__lte=precio_max)
    if categoria:
        qs = qs.filter(producto__categoria=categoria)

    return qs


@login_requerido
def solicitudes(request):
    usuario = get_usuario_sesion(request)
    qs = _filtrar_solicitudes(request)
    
    total      = qs.count()
    pendientes = qs.filter(estado='pendiente').count()
    aceptadas  = qs.filter(estado='aceptada').count()
    pagadas    = qs.filter(estado='pagada').count()
    rechazadas = qs.filter(estado='rechazada').count()

    context = {
        'usuario':    usuario,
        'solicitudes': qs,
        'total':      total,
        'pendientes': pendientes,
        'aceptadas':  aceptadas,
        'pagadas':    pagadas,
        'rechazadas': rechazadas,
        # para repoblar los filtros en el template
        'q':           request.GET.get('q', ''),
        'f_estado':    request.GET.get('estado', ''),
        'f_desde':     request.GET.get('fecha_desde', ''),
        'f_hasta':     request.GET.get('fecha_hasta', ''),
        'f_precio_min': request.GET.get('precio_min', ''),
        'f_precio_max': request.GET.get('precio_max', ''),
        'f_categoria': request.GET.get('categoria', ''),
        'pagina_activa': 'solicitudes',
    }
    return render(request, 'administrador/solicitudes.html', context)


@login_requerido
def solicitudes_export_excel(request):
    qs = _filtrar_solicitudes(request)

    if not qs.exists():
        messages.warning(request, "No hay solicitudes para exportar.")
        return redirect('solicitudes')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Solicitudes"

    # Estilo encabezado
    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")

    headers = ["ID", "Cliente", "Producto", "Vendedor", "CategorÃ­a", "Total ($)", "Abono ($)", "Tipo entrega", "Estado", "Fecha"]
    ws.append(headers)

    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    # Filas
    estado_map = {'pendiente': 'Pendiente', 'aceptada': 'Aceptada', 'pagada': 'Pagada', 'rechazada': 'Rechazada'}
    for s in qs:
        cliente = f"{s.usuario.nombre} {s.usuario.apellido}" if s.usuario else s.nombre_invitado or "Invitado"
        vendedor_nombre = f"{s.producto.vendedor.nombre} {s.producto.vendedor.apellido}"
        ws.append([
            f"#{s.id_solicitud}",
            cliente,
            s.producto.nombre,
            vendedor_nombre,
            s.producto.get_categoria_display(),
            float(s.precio_total),
            float(s.abono),
            s.tipo_entrega,
            estado_map.get(s.estado, s.estado),
            s.fecha_creacion.strftime("%Y-%m-%d"),
        ])

    # Ancho columnas
    anchos = [10, 25, 25, 25, 14, 13, 13, 14, 13, 13]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="solicitudes.xlsx"'
    wb.save(response)
    return response


@login_requerido
def solicitudes_export_pdf(request):
    qs = _filtrar_solicitudes(request)

    if not qs.exists():
        messages.warning(request, "No hay solicitudes para exportar.")
        return redirect('solicitudes')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="solicitudes.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4),
                            leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    # TÃ­tulo
    titulo = Paragraph("<b>Reporte de Solicitudes</b>", styles['Title'])
    elements.append(titulo)
    elements.append(Spacer(1, 12))

    # Tabla
    data = [["ID", "Cliente", "Producto", "Vendedor", "CategorÃ­a", "Total", "Estado", "Fecha"]]
    for s in qs:
        cliente = f"{s.usuario.nombre} {s.usuario.apellido}" if s.usuario else s.nombre_invitado or "Invitado"
        data.append([
            f"#{s.id_solicitud}",
            cliente,
            s.producto.nombre,
            f"{s.producto.vendedor.nombre} {s.producto.vendedor.apellido}",
            s.producto.get_categoria_display(),
            f"${s.precio_total}",
            s.estado.capitalize(),
            s.fecha_creacion.strftime("%Y-%m-%d"),
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE',   (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',       (0, 0), (-1, -1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',  (0, 0), (-1, -1), 20),
    ]))
    elements.append(tabla)

    doc.build(elements)
    return response
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  REPORTE â€” SOLICITUDES POR ESTADO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def reporte_solicitudes_estado(request):
    usuario = get_usuario_sesion(request)
    if not usuario:
        return redirect('inicio')

    por_estado = (
        Solicitudes.objects
        .values('estado')
        .annotate(total=Count('id_solicitud'))
        .order_by('estado')
    )

    total_solicitudes = Solicitudes.objects.count()

    ingresos_totales = (
        Solicitudes.objects
        .filter(estado='pagada')
        .aggregate(total=Sum('precio_total'))['total'] or 0
    )

    conteos    = {item['estado']: item['total'] for item in por_estado}
    pendientes = conteos.get('pendiente', 0)
    aceptadas  = conteos.get('aceptada',  0)
    rechazadas = conteos.get('rechazada', 0)
    pagadas    = conteos.get('pagada',    0)

    def pct(valor):
        if total_solicitudes == 0:
            return 0
        return round((valor / total_solicitudes) * 100, 1)

    ultimas_solicitudes = (
        Solicitudes.objects
        .select_related('usuario', 'producto')
        .order_by('-fecha_creacion')[:10]
    )

    estados_labels  = ['Pendiente', 'Aceptada', 'Rechazada', 'Pagada']
    estados_valores = [pendientes, aceptadas, rechazadas, pagadas]
    estados_colores = ['#F39C12', '#27AE60', '#E74C3C', '#2E75B6']

    context = {
        'usuario':          usuario,
        'pagina_activa':    'reportes',
        'total_solicitudes': total_solicitudes,
        'ingresos_totales': ingresos_totales,
        'pendientes':       pendientes,
        'aceptadas':        aceptadas,
        'rechazadas':       rechazadas,
        'pagadas':          pagadas,
        'pct_pendientes':   pct(pendientes),
        'pct_aceptadas':    pct(aceptadas),
        'pct_rechazadas':   pct(rechazadas),
        'pct_pagadas':      pct(pagadas),
        'ultimas_solicitudes': ultimas_solicitudes,
        'chart_labels':     json.dumps(estados_labels),
        'chart_valores':    json.dumps(estados_valores),
        'chart_colores':    json.dumps(estados_colores),
    }
    return render(request, 'administrador/reporte_solicitudes_estado.html', context)


# â”€â”€ PDF â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_requerido
def reporte_estado_export_pdf(request):
    from reportlab.platypus import HRFlowable
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    total      = Solicitudes.objects.count()
    pendientes = Solicitudes.objects.filter(estado='pendiente').count()
    aceptadas  = Solicitudes.objects.filter(estado='aceptada').count()
    pagadas    = Solicitudes.objects.filter(estado='pagada').count()
    rechazadas = Solicitudes.objects.filter(estado='rechazada').count()
    ingresos   = Solicitudes.objects.filter(
        estado='pagada'
    ).aggregate(t=Sum('precio_total'))['t'] or 0

    def pct(v):
        return f"{round((v/total)*100, 1)}%" if total else "0%"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_solicitudes_estado.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    VINO   = colors.HexColor('#7a2d3e')
    VINO_L = colors.HexColor('#fdf5f5')

    styles  = getSampleStyleSheet()
    elements = []

    titulo_style = ParagraphStyle('titulo', fontSize=18, textColor=VINO,
                                  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    sub_style    = ParagraphStyle('sub', fontSize=10, textColor=colors.HexColor('#888888'),
                                  alignment=TA_CENTER, spaceAfter=16)
    seccion_style = ParagraphStyle('sec', fontSize=12, textColor=colors.HexColor('#2a1010'),
                                   fontName='Helvetica-Bold', spaceAfter=10)

    from datetime import date
    elements.append(Paragraph("CreartSoft â€” Reporte de Solicitudes por Estado", titulo_style))
    elements.append(Paragraph(f"Generado el {date.today().strftime('%d/%m/%Y')}", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=VINO, spaceAfter=20))

    # â”€â”€ tarjetas resumen â”€â”€
    card_data = [[
        Paragraph(f"<b>{total}</b><br/>Total",       styles['Normal']),
        Paragraph(f"<b>{pendientes}</b><br/>Pendientes", styles['Normal']),
        Paragraph(f"<b>{aceptadas}</b><br/>Aceptadas",   styles['Normal']),
        Paragraph(f"<b>{pagadas}</b><br/>Pagadas",        styles['Normal']),
        Paragraph(f"<b>{rechazadas}</b><br/>Rechazadas",  styles['Normal']),
    ]]
    card_table = Table(card_data, colWidths=[3.1*cm]*5)
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#eeeeee')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#FEF3C7')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#D1FAE5')),
        ('BACKGROUND', (3,0), (3,0), colors.HexColor('#DBEAFE')),
        ('BACKGROUND', (4,0), (4,0), colors.HexColor('#FEE2E2')),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',   (0,0), (-1,-1), 11),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ROWHEIGHT',  (0,0), (-1,-1), 40),
        ('BOX',        (0,0), (-1,-1), 0, colors.white),
        ('INNERGRID',  (0,0), (-1,-1), 3, colors.white),
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 20))

    # â”€â”€ tabla distribuciÃ³n SIN barra visual â”€â”€
    elements.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor('#e0c8c8'), spaceAfter=10))
    elements.append(Paragraph("DistribuciÃ³n por estado", seccion_style))

    thin = colors.HexColor('#e0c8c8')
    dist_data = [['Estado', 'Cantidad', 'Porcentaje (%)']]
    for nombre, valor in [('Pendiente', pendientes), ('Aceptada', aceptadas),
                           ('Pagada', pagadas),       ('Rechazada', rechazadas)]:
        dist_data.append([nombre, str(valor), pct(valor)])

    dist_table = Table(dist_data, colWidths=[5*cm, 4*cm, 5*cm])
    dist_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), VINO),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 10),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, VINO_L]),
        ('GRID',           (0,0), (-1,-1), 0.4, thin),
        ('ROWHEIGHT',      (0,0), (-1,-1), 24),
    ]))
    elements.append(dist_table)
    elements.append(Spacer(1, 20))

    # â”€â”€ Ãºltimas 10 solicitudes â”€â”€
    elements.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor('#e0c8c8'), spaceAfter=10))
    elements.append(Paragraph("Ãšltimas 10 solicitudes", seccion_style))

    ultimas = (Solicitudes.objects
               .select_related('usuario', 'producto')
               .order_by('-fecha_creacion')[:10])

    sol_data = [['#', 'Cliente', 'Producto', 'Total', 'Estado', 'Fecha']]
    for s in ultimas:
        cliente = f"{s.usuario.nombre} {s.usuario.apellido}" if s.usuario else "Invitado"
        sol_data.append([
            f"SOL{s.id_solicitud}", cliente, s.producto.nombre,
            f"${s.precio_total:,.0f}", s.estado.capitalize(),
            s.fecha_creacion.strftime("%d/%m/%Y"),
        ])

    sol_table = Table(sol_data, colWidths=[2*cm, 3.5*cm, 3.5*cm, 2.2*cm, 2.3*cm, 2.5*cm])
    sol_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), VINO),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, VINO_L]),
        ('GRID',           (0,0), (-1,-1), 0.4, thin),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(sol_table)
    elements.append(Spacer(1, 16))

    # â”€â”€ pie â”€â”€
    elements.append(HRFlowable(width="100%", thickness=1, color=VINO,
                                spaceBefore=6, spaceAfter=6))
    pie_style = ParagraphStyle('pie', fontSize=8, textColor=colors.HexColor('#aaaaaa'),
                                alignment=TA_CENTER)
    elements.append(Paragraph(
        f"CreartSoft Â· Reporte generado automÃ¡ticamente Â· "
        f"Ingresos confirmados: ${ingresos:,.0f}", pie_style))

    doc.build(elements)
    return response


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  ARCHIVO 2 â€” NUEVO REPORTE: Ingresos por mÃ©todo de pago
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def reporte_metodo_pago(request):
    """
    Reporte: Ingresos por mÃ©todo de pago
    Muestra cuÃ¡nto se ha recaudado y cuÃ¡ntas transacciones se hicieron
    por cada mÃ©todo (tarjeta, PSE, efectivo, transferencia, etc.)
    """
    usuario = get_usuario_sesion(request)

    # â”€â”€ datos principales â”€â”€
    por_metodo = (
        Transacciones.objects
        .values('metodo_pago')
        .annotate(
            total_ingresos=Sum('importe_total'),
            total_transacciones=Count('id_transaccion'),
        )
        .order_by('-total_ingresos')
    )

    total_ingresos     = Transacciones.objects.aggregate(t=Sum('importe_total'))['t'] or 0
    total_transacciones = Transacciones.objects.count()

    # â”€â”€ Ãºltimas 10 transacciones â”€â”€
    ultimas = (
        Transacciones.objects
        .select_related('solicitud__usuario', 'solicitud__producto')
        .order_by('-fecha_creacion')[:10]
    )

    # â”€â”€ JSON para Chart.js â”€â”€
    import json
    labels  = [m['metodo_pago'] or 'Sin especificar' for m in por_metodo]
    valores = [float(m['total_ingresos'] or 0)        for m in por_metodo]
    colores = ['#7a2d3e','#C0392B','#E74C3C','#F39C12','#27AE60','#2E75B6','#8E44AD']

    context = {
        'usuario':             usuario,
        'pagina_activa':       'transacciones',
        'por_metodo':          por_metodo,
        'total_ingresos':      total_ingresos,
        'total_transacciones': total_transacciones,
        'ultimas':             ultimas,
        'chart_labels':        json.dumps(labels),
        'chart_valores':       json.dumps(valores),
        'chart_colores':       json.dumps(colores[:len(labels)]),
    }
    return render(request, 'administrador/reporte_metodo_pago.html', context)


@login_requerido
def reporte_metodo_pago_pdf(request):
    from reportlab.platypus import HRFlowable
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from datetime import date

    por_metodo          = (Transacciones.objects
                           .values('metodo_pago')
                           .annotate(total_ingresos=Sum('importe_total'),
                                     total_transacciones=Count('id_transaccion'))
                           .order_by('-total_ingresos'))
    total_ingresos      = Transacciones.objects.aggregate(t=Sum('importe_total'))['t'] or 0
    total_transacciones = Transacciones.objects.count()

    def pct(v):
        return f"{round((float(v)/float(total_ingresos))*100, 1)}%" if total_ingresos else "0%"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_metodo_pago.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    VINO   = colors.HexColor('#7a2d3e')
    VINO_L = colors.HexColor('#fdf5f5')
    thin   = colors.HexColor('#e0c8c8')
    styles = getSampleStyleSheet()
    elements = []

    titulo_style  = ParagraphStyle('t',  fontSize=18, textColor=VINO,
                                   fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    sub_style     = ParagraphStyle('s',  fontSize=10, textColor=colors.HexColor('#888888'),
                                   alignment=TA_CENTER, spaceAfter=16)
    seccion_style = ParagraphStyle('sc', fontSize=12, textColor=colors.HexColor('#2a1010'),
                                   fontName='Helvetica-Bold', spaceAfter=10)

    elements.append(Paragraph("CreartSoft â€” Ingresos por MÃ©todo de Pago", titulo_style))
    elements.append(Paragraph(f"Generado el {date.today().strftime('%d/%m/%Y')}", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=VINO, spaceAfter=20))

    # â”€â”€ tarjetas resumen â”€â”€
    card_data = [[
        Paragraph(f"<b>${total_ingresos:,.0f}</b><br/>Ingresos totales", styles['Normal']),
        Paragraph(f"<b>{total_transacciones}</b><br/>Transacciones",     styles['Normal']),
        Paragraph(f"<b>{por_metodo.count()}</b><br/>MÃ©todos usados",     styles['Normal']),
    ]]
    card_table = Table(card_data, colWidths=[5*cm, 4*cm, 5*cm])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#D1FAE5')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#DBEAFE')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#FEF3C7')),
        ('ALIGN',  (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ROWHEIGHT', (0,0), (-1,-1), 44),
        ('BOX',      (0,0), (-1,-1), 0, colors.white),
        ('INNERGRID',(0,0), (-1,-1), 3, colors.white),
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 20))

    # â”€â”€ tabla por mÃ©todo â”€â”€
    elements.append(HRFlowable(width="100%", thickness=0.5, color=thin, spaceAfter=10))
    elements.append(Paragraph("Detalle por mÃ©todo de pago", seccion_style))

    met_data = [['MÃ©todo de pago', 'Transacciones', 'Ingresos ($)', 'ParticipaciÃ³n (%)']]
    for m in por_metodo:
        met_data.append([
            m['metodo_pago'] or 'Sin especificar',
            str(m['total_transacciones']),
            f"${m['total_ingresos']:,.0f}",
            pct(m['total_ingresos']),
        ])

    met_table = Table(met_data, colWidths=[4.5*cm, 3.5*cm, 4*cm, 4*cm])
    met_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), VINO),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 10),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, VINO_L]),
        ('GRID',           (0,0), (-1,-1), 0.4, thin),
        ('ROWHEIGHT',      (0,0), (-1,-1), 24),
    ]))
    elements.append(met_table)
    elements.append(Spacer(1, 20))

    # â”€â”€ Ãºltimas 10 transacciones â”€â”€
    elements.append(HRFlowable(width="100%", thickness=0.5, color=thin, spaceAfter=10))
    elements.append(Paragraph("Ãšltimas 10 transacciones", seccion_style))

    ultimas = (Transacciones.objects
               .select_related('solicitud__usuario', 'solicitud__producto')
               .order_by('-fecha_creacion')[:10])

    tx_data = [['#', 'Cliente', 'MÃ©todo', 'Importe ($)', 'Estado', 'Fecha']]
    for t in ultimas:
        cliente = "Invitado"
        if t.solicitud and t.solicitud.usuario:
            cliente = f"{t.solicitud.usuario.nombre} {t.solicitud.usuario.apellido}"
        tx_data.append([
            f"TX{t.id_transaccion}",
            cliente,
            t.metodo_pago or 'â€”',
            f"${t.importe_total:,.0f}",
            t.estado.capitalize(),
            t.fecha_creacion.strftime("%d/%m/%Y"),
        ])

    tx_table = Table(tx_data, colWidths=[2*cm, 3.5*cm, 3*cm, 2.8*cm, 2.2*cm, 2.5*cm])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), VINO),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, VINO_L]),
        ('GRID',           (0,0), (-1,-1), 0.4, thin),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tx_table)
    elements.append(Spacer(1, 16))

    elements.append(HRFlowable(width="100%", thickness=1, color=VINO, spaceBefore=6, spaceAfter=6))
    pie_style = ParagraphStyle('pie', fontSize=8, textColor=colors.HexColor('#aaaaaa'),
                                alignment=TA_CENTER)
    elements.append(Paragraph("CreartSoft Â· Reporte generado automÃ¡ticamente", pie_style))

    doc.build(elements)
    return response


@login_requerido
def reporte_metodo_pago_excel(request):
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Border, Side
    from openpyxl.chart import DoughnutChart, Reference
    from openpyxl.chart.series import DataPoint
    from datetime import date

    por_metodo          = (Transacciones.objects
                           .values('metodo_pago')
                           .annotate(total_ingresos=Sum('importe_total'),
                                     total_transacciones=Count('id_transaccion'))
                           .order_by('-total_ingresos'))
    total_ingresos      = Transacciones.objects.aggregate(t=Sum('importe_total'))['t'] or 0
    total_transacciones = Transacciones.objects.count()

    wb  = openpyxl.Workbook()
    ws  = wb.active
    ws.title = "Ingresos por mÃ©todo"
    ws.sheet_view.showGridLines = False

    VINO   = "7a2d3e"
    VINO_L = "fdf5f5"
    BLANCO = "FFFFFF"
    h_font = Font(name='Calibri', bold=True, color=BLANCO, size=11)
    h_fill = PatternFill("solid", fgColor=VINO)
    h_alig = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin   = Side(style='thin', color='e0c8c8')
    borde  = Border(left=thin, right=thin, top=thin, bottom=thin)

    # tÃ­tulo
    ws.merge_cells('A1:E1')
    ws['A1'] = 'CreartSoft â€” Ingresos por MÃ©todo de Pago'
    ws['A1'].font = Font(name='Calibri', bold=True, size=15, color=VINO)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 34

    ws.merge_cells('A2:E2')
    ws['A2'] = f'Generado el {date.today().strftime("%d/%m/%Y")}'
    ws['A2'].font = Font(name='Calibri', size=10, color='888888')
    ws['A2'].alignment = Alignment(horizontal='center')
    ws.row_dimensions[2].height = 16

    # tarjetas fila 4-5
    tarjetas = [
        ('Ingresos totales', f"${total_ingresos:,.0f}", "D1FAE5", "065F46"),
        ('Transacciones',    str(total_transacciones),  "DBEAFE", "1E3A8A"),
        ('MÃ©todos usados',   str(por_metodo.count()),   "FEF3C7", "92400E"),
    ]
    ws.row_dimensions[4].height = 14
    ws.row_dimensions[5].height = 28
    ws.row_dimensions[6].height = 16
    ws.row_dimensions[7].height = 14

    for ci, (label, valor, bg, fg) in enumerate(tarjetas, 1):
        c_val = ws.cell(row=5, column=ci, value=valor)
        c_val.font  = Font(name='Calibri', bold=True, size=13, color=fg)
        c_val.fill  = PatternFill("solid", fgColor=bg)
        c_val.alignment = Alignment(horizontal='center', vertical='center')
        c_val.border = borde
        c_lbl = ws.cell(row=6, column=ci, value=label)
        c_lbl.font  = Font(name='Calibri', size=9, color=fg)
        c_lbl.fill  = PatternFill("solid", fgColor=bg)
        c_lbl.alignment = Alignment(horizontal='center', vertical='center')
        c_lbl.border = borde

    # tabla por mÃ©todo (fila 9)
    ws.row_dimensions[9].height = 20
    headers = ['MÃ©todo de pago', 'Transacciones', 'Ingresos ($)', 'ParticipaciÃ³n (%)']
    for ci, h in enumerate(headers, 1):
        c = ws.cell(row=9, column=ci, value=h)
        c.font = h_font; c.fill = h_fill
        c.alignment = h_alig; c.border = borde

    colores_fila = ["FEF3C7","D1FAE5","DBEAFE","FEE2E2","EDE9FE","FCE7F3","F0FDF4"]
    for ri, m in enumerate(por_metodo, 10):
        ws.row_dimensions[ri].height = 18
        ing = float(m['total_ingresos'] or 0)
        participacion = round((ing / float(total_ingresos)) * 100, 1) if total_ingresos else 0
        bg = colores_fila[(ri - 10) % len(colores_fila)]
        fila = [m['metodo_pago'] or 'Sin especificar',
                m['total_transacciones'], ing, participacion]
        for ci, valor in enumerate(fila, 1):
            c = ws.cell(row=ri, column=ci, value=valor)
            c.fill = PatternFill("solid", fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')
            c.border = borde
            c.font = Font(name='Calibri', size=10)
            if ci == 3:
                c.number_format = '$#,##0.00'
            if ci == 4:
                c.number_format = '0.0"%"'

    # grÃ¡fica de dona
    last_row = 9 + por_metodo.count()
    chart = DoughnutChart()
    chart.title = "Ingresos por mÃ©todo de pago"
    chart.style = 10
    chart.hole_size = 50
    data_ref   = Reference(ws, min_col=3, min_row=9, max_row=last_row)
    labels_ref = Reference(ws, min_col=1, min_row=10, max_row=last_row)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(labels_ref)
    slice_colors = ['7a2d3e','C0392B','E74C3C','F39C12','27AE60','2E75B6','8E44AD']
    for i in range(min(por_metodo.count(), len(slice_colors))):
        pt = DataPoint(idx=i)
        pt.graphicalProperties.solidFill = slice_colors[i]
        chart.series[0].dPt.append(pt)
    chart.width = 14; chart.height = 10
    ws.add_chart(chart, "F9")

    # anchos
    for col, ancho in zip(range(1, 6), [22, 16, 16, 18, 2]):
        ws.column_dimensions[get_column_letter(col)].width = ancho

    # hoja 2 â€” Ãºltimas transacciones
    ws2 = wb.create_sheet("Ãšltimas transacciones")
    ws2.sheet_view.showGridLines = False
    ws2.merge_cells('A1:F1')
    ws2['A1'] = 'Ãšltimas 10 transacciones'
    ws2['A1'].font = Font(name='Calibri', bold=True, size=13, color=VINO)
    ws2['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws2.row_dimensions[1].height = 28

    headers2 = ['# Trans.', 'Cliente', 'MÃ©todo', 'Importe ($)', 'Estado', 'Fecha']
    for ci, h in enumerate(headers2, 1):
        c = ws2.cell(row=2, column=ci, value=h)
        c.font = h_font; c.fill = h_fill
        c.alignment = h_alig; c.border = borde
    ws2.row_dimensions[2].height = 20

    ultimas = (Transacciones.objects
               .select_related('solicitud__usuario', 'solicitud__producto')
               .order_by('-fecha_creacion')[:10])

    for ri, t in enumerate(ultimas, 3):
        cliente = "Invitado"
        if t.solicitud and t.solicitud.usuario:
            cliente = f"{t.solicitud.usuario.nombre} {t.solicitud.usuario.apellido}"
        bg = BLANCO if ri % 2 == 0 else VINO_L
        fila = [f"TX{t.id_transaccion}", cliente, t.metodo_pago or 'â€”',
                float(t.importe_total), t.estado.capitalize(),
                t.fecha_creacion.strftime("%d/%m/%Y")]
        ws2.row_dimensions[ri].height = 18
        for ci, valor in enumerate(fila, 1):
            c = ws2.cell(row=ri, column=ci, value=valor)
            c.fill = PatternFill("solid", fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')
            c.border = borde
            c.font = Font(name='Calibri', size=10)
            if ci == 4:
                c.number_format = '$#,##0.00'

    for col, ancho in zip(range(1, 7), [12, 24, 18, 14, 12, 13]):
        ws2.column_dimensions[get_column_letter(col)].width = ancho

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_metodo_pago.xlsx"'
    wb.save(response)
    return response
# â”€â”€ EXCEL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_requerido
def reporte_estado_export_excel(request):
    from openpyxl.utils import get_column_letter
    from openpyxl.chFart import DoughnutChart, Reference
    from openpyxl.chart.series import DataPoint
    from datetime import date

    total      = Solicitudes.objects.count()
    pendientes = Solicitudes.objects.filter(estado='pendiente').count()
    aceptadas  = Solicitudes.objects.filter(estado='aceptada').count()
    pagadas    = Solicitudes.objects.filter(estado='pagada').count()
    rechazadas = Solicitudes.objects.filter(estado='rechazada').count()
    ingresos   = Solicitudes.objects.filter(
        estado='pagada'
    ).aggregate(t=Sum('precio_total'))['t'] or 0

    def pct(v):
        return round((v/total)*100, 1) if total else 0

    wb = openpyxl.Workbook()

    # â”€â”€ HOJA 1 â€” RESUMEN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    ws = wb.active
    ws.title = "Resumen"
    ws.sheet_view.showGridLines = False

    VINO     = "7a2d3e"
    VINO_L   = "fdf5f5"
    AMARILLO = "FEF3C7"
    VERDE    = "D1FAE5"
    AZUL     = "DBEAFE"
    ROJO_L   = "FEE2E2"
    BLANCO   = "FFFFFF"
    GRIS     = "f5f5f5"

    h_font = Font(name='Calibri', bold=True, color=BLANCO, size=11)
    h_fill = PatternFill("solid", fgColor=VINO)
    h_alig = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin   = Side(style='thin', color='e0c8c8')
    borde  = Border(left=thin, right=thin, top=thin, bottom=thin)

    # â€” tÃ­tulo â€”
    ws.merge_cells('A1:G1')
    ws['A1']           = 'CreartSoft â€” Reporte de Solicitudes por Estado'
    ws['A1'].font      = Font(name='Calibri', bold=True, size=16, color=VINO)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 36

    ws.merge_cells('A2:G2')
    ws['A2']           = f'Generado el {date.today().strftime("%d/%m/%Y")}'
    ws['A2'].font      = Font(name='Calibri', size=10, color='888888')
    ws['A2'].alignment = Alignment(horizontal='center')
    ws.row_dimensions[2].height = 18

    # â€” tarjetas â€”
    tarjetas = [
        ('Total',      total,      GRIS,    '555555'),
        ('Pendientes', pendientes, AMARILLO,'92400E'),
        ('Aceptadas',  aceptadas,  VERDE,   '065F46'),
        ('Pagadas',    pagadas,    AZUL,    '1E3A8A'),
        ('Rechazadas', rechazadas, ROJO_L,  '991B1B'),
    ]
    ws.row_dimensions[4].height = 14
    ws.row_dimensions[5].height = 30
    ws.row_dimensions[6].height = 18
    ws.row_dimensions[7].height = 14

    for col, (label, valor, bg, fg) in enumerate(tarjetas, 1):
        c_val           = ws.cell(row=5, column=col, value=valor)
        c_val.font      = Font(name='Calibri', bold=True, size=16, color=fg)
        c_val.fill      = PatternFill("solid", fgColor=bg)
        c_val.alignment = Alignment(horizontal='center', vertical='center')
        c_val.border    = borde

        c_lbl           = ws.cell(row=6, column=col, value=label)
        c_lbl.font      = Font(name='Calibri', size=9, color=fg)
        c_lbl.fill      = PatternFill("solid", fgColor=bg)
        c_lbl.alignment = Alignment(horizontal='center', vertical='center')
        c_lbl.border    = borde

    # â€” ingreso especial col 6 â€”
    c_ing               = ws.cell(row=5, column=6, value=float(ingresos))
    c_ing.number_format = '$#,##0'
    c_ing.font          = Font(name='Calibri', bold=True, size=14, color='065F46')
    c_ing.fill          = PatternFill("solid", fgColor=VERDE)
    c_ing.alignment     = Alignment(horizontal='center', vertical='center')
    c_ing.border        = borde

    c_lbl2              = ws.cell(row=6, column=6, value='Ingresos confirmados')
    c_lbl2.font         = Font(name='Calibri', size=9, color='065F46')
    c_lbl2.fill         = PatternFill("solid", fgColor=VERDE)
    c_lbl2.alignment    = Alignment(horizontal='center', vertical='center')
    c_lbl2.border       = borde

    # â€” tabla distribuciÃ³n (fila 9) â€”
    ws.row_dimensions[9].height = 20
    for ci, h in enumerate(['Estado', 'Cantidad', 'Porcentaje (%)'], 1):
        c           = ws.cell(row=9, column=ci, value=h)
        c.font      = h_font
        c.fill      = h_fill
        c.alignment = h_alig
        c.border    = borde

    estados_data = [
        ('Pendiente', pendientes),
        ('Aceptada',  aceptadas),
        ('Pagada',    pagadas),
        ('Rechazada', rechazadas),
    ]
    colores_fila = [AMARILLO, VERDE, AZUL, ROJO_L]

    for ri, ((nombre, valor), bg) in enumerate(zip(estados_data, colores_fila), 10):
        ws.row_dimensions[ri].height = 18
        for ci, dato in enumerate([nombre, valor, pct(valor)], 1):
            c           = ws.cell(row=ri, column=ci, value=dato)
            c.fill      = PatternFill("solid", fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')
            c.border    = borde
            c.font      = Font(name='Calibri', size=10)
            if ci == 3:
                c.number_format = '0.0"%"'

    # â€” grÃ¡fica de dona â€”
    chart           = DoughnutChart()
    chart.title     = "DistribuciÃ³n por Estado"
    chart.style     = 10
    chart.hole_size = 50

    data_ref   = Reference(ws, min_col=2, min_row=9, max_row=13)
    labels_ref = Reference(ws, min_col=1, min_row=10, max_row=13)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(labels_ref)

    for i, color_hex in enumerate(['F39C12', '27AE60', '2E75B6', 'E74C3C']):
        pt = DataPoint(idx=i)
        pt.graphicalProperties.solidFill = color_hex
        chart.series[0].dPt.append(pt)

    chart.width  = 14
    chart.height = 10
    ws.add_chart(chart, "E9")

    for col, ancho in zip(range(1, 8), [14, 12, 16, 2, 2, 20, 2]):
        ws.column_dimensions[get_column_letter(col)].width = ancho

    # â”€â”€ HOJA 2 â€” ÃšLTIMAS SOLICITUDES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    ws2 = wb.create_sheet("Ãšltimas solicitudes")
    ws2.sheet_view.showGridLines = False

    ws2.merge_cells('A1:F1')
    ws2['A1']           = 'Ãšltimas 10 solicitudes'
    ws2['A1'].font      = Font(name='Calibri', bold=True, size=13, color=VINO)
    ws2['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws2.row_dimensions[1].height = 28

    for ci, h in enumerate(['# Solicitud', 'Cliente', 'Producto', 'Total ($)', 'Estado', 'Fecha'], 1):
        c           = ws2.cell(row=2, column=ci, value=h)
        c.font      = h_font
        c.fill      = h_fill
        c.alignment = h_alig
        c.border    = borde
    ws2.row_dimensions[2].height = 20

    ultimas = Solicitudes.objects.select_related('usuario', 'producto').order_by('-fecha_creacion')[:10]
    for ri, s in enumerate(ultimas, 3):
        cliente            = f"{s.usuario.nombre} {s.usuario.apellido}" if s.usuario else "Invitado"
        bg                 = BLANCO if ri % 2 == 0 else VINO_L
        fila               = [
            f"SOL{s.id_solicitud}", cliente, s.producto.nombre,
            float(s.precio_total), s.estado.capitalize(),
            s.fecha_creacion.strftime("%d/%m/%Y"),
        ]
        ws2.row_dimensions[ri].height = 18
        for ci, valor in enumerate(fila, 1):
            c           = ws2.cell(row=ri, column=ci, value=valor)
            c.fill      = PatternFill("solid", fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')
            c.border    = borde
            c.font      = Font(name='Calibri', size=10)
            if ci == 4:
                c.number_format = '$#,##0'

    for col, ancho in zip(range(1, 7), [14, 24, 24, 14, 12, 13]):
        ws2.column_dimensions[get_column_letter(col)].width = ancho

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_solicitudes_estado.xlsx"'
    wb.save(response)
    return response

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PQRS (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def pqrs(request):
    usuario = get_usuario_sesion(request)

    qs = _filtrar_pqrs(request)  #esto reemplaza el queryset fijo

    pendientes = PQRS.objects.filter(estado_respuesta='sin_respuesta').count()
    resueltos  = PQRS.objects.filter(estado_respuesta='respondido').count()

    context = {
        'usuario': usuario,
        'pqrs_list': qs,
        'total_pqrs': qs.count(),
        'pendientes': pendientes,
        'resueltos': resueltos,
        'pagina_activa': 'pqrs',
        'q': request.GET.get('q', ''),  # para que el input mantenga el texto escrito
    }
    return render(request, 'administrador/pqrs.html', context)

# acciones --------------------------------------------------------------------------------->
# acciones --------------------------------------------------------------------------------->
# acciones --------------------------------------------------------------------------------->

@login_requerido
def pqrs_responder(request):
    if request.method == 'POST':
        try:
            pk = request.POST.get('pqrs_id')
            pqrs_obj = get_object_or_404(PQRS, pk=pk)

            pqrs_obj.respuesta = request.POST.get('respuesta', '')
            pqrs_obj.estado_respuesta = 'respondido'
            pqrs_obj.save()
            correo_respuesta_pqrs(pqrs_obj)
            messages.success(request, "PQRS respondida excitosamente")
        except Exception as e:
            messages.error(request, "Ocurrio un error al responder la pqrs, intentelo de nuevo.")


    return redirect('pqrs')

@login_requerido
def gestionar_cambio_perfil(request, id_pqrs):
    pqrs = get_object_or_404(PQRS, id_pqrs=id_pqrs)

    if request.method == "POST":
        try:
            accion = request.POST.get('accion')

            if accion == "aceptar":
                # AQUÃ aplicas los cambios al usuario
                usuario = pqrs.usuario

                # OJO: tu mensaje es texto, no JSON
                # asÃ­ que toca parsearlo manual (simple)
                lineas = pqrs.mensaje.split("\n")

                campo_actual = None
                nuevos_datos = {}

                for linea in lineas:
                    if ":" in linea and "Antes" not in linea and "Nuevo" not in linea:
                        campo_actual = linea.replace(":", "").strip()

                    if "Nuevo:" in linea and campo_actual:
                        valor = linea.replace("Nuevo:", "").strip()
                        nuevos_datos[campo_actual] = valor

                # aplicar cambios
                for campo, valor in nuevos_datos.items():
                    if hasattr(usuario, campo):
                        setattr(usuario, campo, valor)

                usuario.save()

                pqrs.respuesta = "Solicitud aceptada. Perfil actualizado correctamente."
                pqrs.estado_respuesta = "respondido"
                pqrs.save()
                messages.success(request, "Solicitud permitida con excito.")

            elif accion == "rechazar":
                pqrs.respuesta = "Solicitud rechazada por el administrador."
                pqrs.estado_respuesta = "respondido"
                pqrs.save()
                messages.info(request,"Solicitud denegada.")

        except Exception as e:
            messages.error(request, "Ocurrio un error al responder la pqrs de cambio de perfil, intentelo de nuevo.")

    return redirect('pqrs')

def _filtrar_pqrs(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()

    qs = PQRS.objects.select_related('usuario').order_by('-id_pqrs')

    if q:
        qs = qs.filter(
            Q(asunto__icontains=q) |
            Q(usuario__nombre__icontains=q) |
            Q(usuario__apellido__icontains=q)
        )
    if estado:
        qs = qs.filter(estado_respuesta=estado)

    return qs


@login_requerido
def pqrs_export_excel(request):
    qs = _filtrar_pqrs(request)

    if not qs.exists():
        messages.warning(request, "No hay pqrs para exportar.")
        return redirect('pqrs')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PQRS"

    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")

    headers = ["ID", "Asunto", "Mensaje", "Categoria", "Estado", "Respuesta", "Usuario"]
    ws.append(headers)
    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    for p in qs:
        usuario = f"{p.usuario.nombre} {p.usuario.apellido}" if p.usuario else ''
        ws.append([
            f"#{p.id_pqrs}",
            p.asunto,
            p.mensaje,
            p.categoria.capitalize(),
            p.estado_respuesta.replace('_', ' ').capitalize(),
            p.respuesta or '',
            usuario
        ])

    anchos = [10, 30, 40, 14, 16, 40, 25]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="pqrs.xlsx"'
    wb.save(response)
    return response


@login_requerido
def pqrs_export_pdf(request):
    qs = _filtrar_pqrs(request)

    if not qs.exists():
        messages.warning(request, "No hay pqrs para exportar.")
        return redirect('pqrs')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pqrs.pdf"'

    doc      = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = [Paragraph("<b>Reporte de PQRS</b>", styles['Title']), Spacer(1, 12)]

    data = [["ID", "Asunto", "Categoria", "Estado", "Usuario", "Fecha"]]
    for p in qs:
        usuario = f"{p.usuario.nombre} {p.usuario.apellido}" if p.usuario else ''
        data.append([
            f"#{p.id_pqrs}",
            p.asunto,
            p.categoria.capitalize(),
            p.estado_respuesta.replace('_', ' ').capitalize(),
            usuario,
            p.fecha_creacion.strftime("%Y-%m-%d") if p.fecha_creacion else ''
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    doc.build(elements)
    return 

@login_requerido
def gestionar_edicion_producto(request, id_pqrs):
    pqrs = get_object_or_404(PQRS, id_pqrs=id_pqrs)

    if request.method == "POST":
        accion = request.POST.get('accion')

        try:
            id_producto = int(pqrs.asunto.split('#')[-1].strip())
        except (ValueError, IndexError):
            messages.error(request, "No se pudo identificar el producto.")
            return redirect('pqrs')

        producto = get_object_or_404(Productos, id_producto=id_producto)

        if accion == "aceptar":
            lineas = pqrs.mensaje.split("\n")
            campo_actual = None
            nuevos_datos = {}

            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue

                if ":" in linea and "Antes:" not in linea and "Nuevo:" not in linea:
                    campo_actual = linea.replace(":", "").strip()

                elif "Nuevo:" in linea and campo_actual:
                    valor = linea.replace("Nuevo:", "").strip()
                    nuevos_datos[campo_actual] = valor

            for campo, valor in nuevos_datos.items():
                if campo in ['nombre', 'descripcion', 'precio', 'categoria']:
                    setattr(producto, campo, valor)

            producto.save()

            pqrs.respuesta = "Solicitud de ediciÃ³n aceptada. Producto actualizado."
            pqrs.estado_respuesta = "respondido"
            pqrs.save()

            messages.success(request, "Producto actualizado correctamente.")

        elif accion == "rechazar":
            pqrs.respuesta = "Solicitud de ediciÃ³n rechazada."
            pqrs.estado_respuesta = "respondido"
            pqrs.save()

            messages.info(request, "Solicitud rechazada.")

    return redirect('pqrs')
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PERFIL (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def administrador_perfil(request):
    usuario = get_usuario_sesion(request)

    if request.method == 'POST':
        try:
            usuario.nombre = request.POST.get('nombre', usuario.nombre)
            usuario.apellido = request.POST.get('apellido', usuario.apellido)
            usuario.correo = request.POST.get('correo', usuario.correo)
            usuario.numero = request.POST.get('numero', usuario.numero)
            usuario.direccion = request.POST.get('direccion', usuario.direccion)

            nueva = request.POST.get('nueva_contrasena', '').strip()
            if nueva:
                usuario.contrasena = make_password(nueva)

            usuario.save()
            messages.success(request, "Perfil actualizado con excito")
            request.session['usuario_nombre'] = usuario.nombre
            return redirect('administrador_perfil')
        
        except Exception as e:
            messages.error(request, "Algo saliÃ³ mal en la actualizacion del perfil. Intentelo de nuevo.")

    context = {
        'usuario': usuario,
        'pagina_activa': 'perfil',
    }
    return render(request, 'administrador/administrador_perfil.html', context)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  INVENTARIO (ADMIN)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def inventario_admin(request):
    usuario = get_usuario_sesion(request)

    q = request.GET.get('q', '').strip()
    proveedor_filtro = request.GET.get('id_proveedor', '').strip()

    inventario = Inventario.objects.select_related('id_proveedor').filter(estado=True)
    
    if q:
        inventario = inventario.filter(nombre__icontains=q)
    if proveedor_filtro:
        inventario = inventario.filter(id_proveedor__nombre__icontains=proveedor_filtro)

    proveedores = Proveedores.objects.filter(estado=True).prefetch_related('inventario_set')

    return render(request, 'administrador/inventario.html', {
        'inventario': inventario,
        'proveedores': proveedores,
        'usuario': usuario,
    })

#acciones --------------------------------------------------------------------------------------
#acciones --------------------------------------------------------------------------------------
#acciones --------------------------------------------------------------------------------------
#acciones --------------------------------------------------------------------------------------

@login_requerido
def crear_elemento_inventario(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get("nombre")
            categoria = request.POST.get("categoria")
            proveedor_id = request.POST.get("nombre_proveedor")
            cantidad = request.POST.get("cantidad")
            unidad = request.POST.get("unidad")
            stock_minimo = request.POST.get("stock_minimo")
            precio_unitario = request.POST.get("precio_unitario")

            if not all([nombre, categoria, proveedor_id, cantidad, unidad, stock_minimo, precio_unitario]):
                messages.warning(request, "Se necesitan todos los datos llenos")
                return redirect('inventario')

            proveedor = Proveedores.objects.get(id_proveedor=proveedor_id)

            Inventario.objects.create(
                nombre=nombre,
                categoria=categoria,
                id_proveedor=proveedor,
                cantidad=cantidad,
                unidad=unidad,
                stock_minimo=stock_minimo,
                precio_unitario=precio_unitario,
            )
            messages.success(request, "Elemento creado exitosamente")

        except Exception as e:
            messages.error(request, "Algo saliÃ³ mal, intentalo de nuevo")

    return redirect('inventario')

@login_requerido
def crear_proveedor(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            empresa = request.POST.get("empresa")
            numero = request.POST.get("telefono")
            correo = request.POST.get("correo")
            direccion = request.POST.get("direccion")

            if not all([nombre, empresa, numero, correo, direccion]):
                messages.warning(request, "Se necesitan todos los datos llenos")
                return redirect('inventario')
   
            Proveedores.objects.create(
                nombre=nombre,
                apellido=apellido,
                empresa=empresa,
                numero=numero,
                correo=correo,
                direccion=direccion,
            )
            messages.success(request, "Proveedor creado exitosamente")

        except Exception as e:
            messages.error(request, "Algo saliÃ³ mal, intentalo de nuevo")

    return redirect('inventario')

@login_requerido
def modificar_producto_inventario(request, id_inventario):
    elemento = get_object_or_404(Inventario, id_inventario=id_inventario)

    if request.method == "POST":
        try:
            nombre = request.POST.get("nombre")
            categoria = request.POST.get("categoria")
            proveedor_id = request.POST.get("nombre_proveedor")
            stock_minimo = request.POST.get("stock_minimo")
            precio_unitario = request.POST.get("precio_unitario")
            cantidad = request.POST.get("cantidad")

            if not all([nombre, categoria, proveedor_id, stock_minimo, precio_unitario, cantidad]):
                messages.warning(request, "Se necesitan todos los datos llenos")
                return redirect('inventario')

            elemento.nombre = nombre
            elemento.categoria = categoria
            elemento.id_proveedor_id = proveedor_id
            elemento.stock_minimo = stock_minimo
            elemento.precio_unitario = precio_unitario
            elemento.cantidad = cantidad
            elemento.save()
            messages.success(request, "Elemento modificado exitosamente")

        except Exception as e:
            messages.error(request, "Algo saliÃ³ mal, intentalo de nuevo")

    return redirect('inventario')

@login_requerido
def inhactivar_elemento_inventario(request, id_inventario):
    elemento = get_object_or_404(Inventario, id_inventario=id_inventario)
    if request.method == "POST":
        try:
            elemento = get_object_or_404(Inventario, id_inventario=id_inventario)

            elemento.estado = not elemento.estado
            elemento.save()
            messages.success(request, "Elemento inhabilitado. Se notificÃ³ al vendedor para cerrar productos.")
        
        except Exception as e:
            messages.error(request, "Error al cambiar estado. Intentalo de nuevo")

    return redirect("inventario")

@login_requerido
def modificar_proveedor(request, id_proveedor):
    proveedor = get_object_or_404(Proveedores, id_proveedor=id_proveedor)

    if request.method == "POST":
        try:
            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            empresa = request.POST.get("empresa")
            numero = request.POST.get("telefono")
            correo = request.POST.get("correo")
            direccion = request.POST.get("direccion")

            if not all([nombre, apellido, empresa, numero, correo]):
                messages.warning(request, "Se necesitan todos los datos llenos")
                return redirect('inventario')

            proveedor.nombre = nombre
            proveedor.apellido = apellido
            proveedor.empresa = empresa
            proveedor.numero = numero
            proveedor.correo = correo
            proveedor.direccion = direccion
            proveedor.save()
            messages.success(request, "Proveedor actualizado exitosamente")

        except Exception as e:
            messages.error(request, "Algo saliÃ³ mal, intentalo de nuevo")

    return redirect('inventario')

@login_requerido
def inhactivar_proveedor(request, id_proveedor):
    proveedor = get_object_or_404(Proveedores, id_proveedor=id_proveedor)
    if request.method == "POST":
        try:
            proveedor = get_object_or_404(Proveedores, id_proveedor=id_proveedor)

            proveedor.estado = not proveedor.estado
            proveedor.save()
            messages.success(request, "Proveedor inhabilitado")
        
        except Exception as e:
            messages.error(request, "Error al cambiar estado. Intentalo de nuevo")

    return redirect("inventario")

def _filtrar_inventario(request):
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    qs = Inventario.objects.select_related('id_proveedor').order_by('-id_inventario')

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(id_proveedor__empresa__icontains=q)
        )
    if categoria:
        qs = qs.filter(categoria=categoria)

    return qs


@login_requerido
def inventario_export_excel(request):
    qs = _filtrar_inventario(request)

    if not qs.exists():
        messages.warning(request, "No hay elementos en el inventario para exportar.")
        return redirect('inventario')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"

    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")

    headers = ["ID", "Nombre", "Categoria", "Proveedor", "Stock Actual", "Stock Minimo", "Unidad de medida"]
    ws.append(headers)
    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    for e in qs:
        proveedor = e.id_proveedor.empresa if e.id_proveedor else ''
        ws.append([
            f"#{e.id_inventario}",
            e.nombre,
            e.categoria.capitalize(),
            proveedor,
            e.cantidad,
            e.stock_minimo,
            e.unidad,
        ])

    anchos = [10, 30, 20, 25, 15, 15, 15]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    wb.save(response)
    return response


@login_requerido
def inventario_export_pdf(request):
    qs = _filtrar_inventario(request)

    if not qs.exists():
        messages.warning(request, "No hay elementos en el inventario para exportar.")
        return redirect('inventario')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventario.pdf"'

    doc      = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = [Paragraph("<b>Reporte de Inventario</b>", styles['Title']), Spacer(1, 12)]

    data = [["ID", "Nombre", "Categoria", "Proveedor", "Stock Actual", "Stock Minimo", "Unidad"]]
    for e in qs:
        proveedor = e.id_proveedor.empresa if e.id_proveedor else ''
        data.append([
            f"#{e.id_inventario}",
            e.nombre,
            e.categoria.capitalize(),
            proveedor,
            e.cantidad,
            e.stock_minimo,
            e.unidad,
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    doc.build(elements)
    return response
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  REPORTES DE INVENTARIO â€” anÃ¡lisis para toma de decisiones
#  Pega estas funciones en views.py y agrega las URLs correspondientes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def inventario_export_excel(request):
    """
    Reporte Excel con anÃ¡lisis real:
    - Por cada ingrediente: cuÃ¡ntas solicitudes usan productos que lo contienen
    - Movimientos de salida vs merma
    - Costo total consumido
    - Veredicto: rentable / revisar / eliminar
    """
    from django.db.models import Count, Sum
    from .models import Inventario, Movimiento, RecetaProducto, Solicitudes

    qs = Inventario.objects.select_related('id_proveedor').order_by('categoria', 'nombre')

    wb = openpyxl.Workbook()

    # â•â• HOJA 1: RESUMEN POR INGREDIENTE â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    ws1 = wb.active
    ws1.title = "AnÃ¡lisis Ingredientes"

    header_fill  = PatternFill("solid", fgColor="7a2d3e")
    verde_fill   = PatternFill("solid", fgColor="C6EFCE")
    amarillo_fill = PatternFill("solid", fgColor="FFEB9C")
    rojo_fill    = PatternFill("solid", fgColor="FFC7CE")
    header_font  = Font(color="FFFFFF", bold=True, size=10)
    center       = Alignment(horizontal="center", vertical="center")

    headers = [
        "Ingrediente", "CategorÃ­a", "Proveedor",
        "Stock actual", "Stock mÃ­n.", "Unidad",
        "Precio unit. ($)",
        "Salidas reales", "Mermas", "% Merma",
        "Costo merma ($)", "Costo total consumido ($)",
        "Productos que lo usan", "Solicitudes relacionadas",
        "Veredicto"
    ]
    ws1.append(headers)
    for col, _ in enumerate(headers, 1):
        c = ws1.cell(row=1, column=col)
        c.fill = header_fill
        c.font = header_font
        c.alignment = center

    for ing in qs:
        # Movimientos
        salidas = Movimiento.objects.filter(
            id_inventario=ing, tipo='salida'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        mermas = Movimiento.objects.filter(
            id_inventario=ing, tipo='merma'
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        total_consumido = salidas + mermas
        porcentaje_merma = round((mermas / total_consumido * 100), 1) if total_consumido > 0 else 0
        costo_merma = round(float(ing.precio_unitario) * mermas, 2)
        costo_total = round(float(ing.precio_unitario) * total_consumido, 2)

        # Productos que usan este ingrediente
        productos_count = RecetaProducto.objects.filter(
            ingrediente=ing, estado=True
        ).values('producto').distinct().count()

        # Solicitudes de esos productos (pagadas o aceptadas = reales)
        solicitudes_count = Solicitudes.objects.filter(
            producto__receta__ingrediente=ing,
            estado__in=['pagada', 'aceptada']
        ).distinct().count()

        # Veredicto
        if solicitudes_count == 0 and productos_count == 0:
            veredicto = "âŒ Eliminar â€” sin uso"
        elif porcentaje_merma > 40:
            veredicto = "âš ï¸ Revisar â€” alta merma"
        elif ing.cantidad < ing.stock_minimo:
            veredicto = "âš ï¸ Reabastecer urgente"
        elif solicitudes_count > 5:
            veredicto = "âœ… Rentable"
        elif solicitudes_count > 0:
            veredicto = "âœ… En uso"
        else:
            veredicto = "âš ï¸ Revisar â€” poca demanda"

        fila = [
            ing.nombre,
            ing.categoria,
            ing.id_proveedor.empresa if ing.id_proveedor else 'â€”',
            ing.cantidad,
            ing.stock_minimo,
            ing.unidad,
            float(ing.precio_unitario),
            salidas,
            mermas,
            f"{porcentaje_merma}%",
            costo_merma,
            costo_total,
            productos_count,
            solicitudes_count,
            veredicto,
        ]
        ws1.append(fila)
        row_num = ws1.max_row

        # Color de fila segÃºn veredicto
        if "Eliminar" in veredicto:
            fill = rojo_fill
        elif "Revisar" in veredicto or "Reabastecer" in veredicto:
            fill = amarillo_fill
        else:
            fill = verde_fill

        for col in range(1, len(headers) + 1):
            ws1.cell(row=row_num, column=col).fill = fill
            ws1.cell(row=row_num, column=col).alignment = center

    anchos = [22, 14, 20, 12, 10, 8, 14, 12, 8, 10, 14, 18, 16, 16, 22]
    for i, w in enumerate(anchos, 1):
        ws1.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    # â•â• HOJA 2: HISTORIAL DE MOVIMIENTOS â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    ws2 = wb.create_sheet("Movimientos")

    headers2 = ["Ingrediente", "CategorÃ­a", "Tipo", "Cantidad", "Unidad", "Costo unit.", "Costo total", "ObservaciÃ³n", "Fecha"]
    ws2.append(headers2)
    for col, _ in enumerate(headers2, 1):
        c = ws2.cell(row=1, column=col)
        c.fill = header_fill
        c.font = header_font
        c.alignment = center

    movimientos = Movimiento.objects.select_related('id_inventario').order_by('-fecha')
    for m in movimientos:
        costo = round(float(m.id_inventario.precio_unitario) * m.cantidad, 2) if m.costo_unitario is None else float(m.costo_unitario) * m.cantidad
        ws2.append([
            m.id_inventario.nombre,
            m.id_inventario.categoria,
            m.tipo.capitalize(),
            m.cantidad,
            m.id_inventario.unidad,
            float(m.id_inventario.precio_unitario),
            costo,
            m.observacion or 'â€”',
            m.fecha.strftime("%Y-%m-%d %H:%M"),
        ])
        row_num = ws2.max_row
        if m.tipo == 'merma':
            for col in range(1, 10):
                ws2.cell(row=row_num, column=col).fill = rojo_fill
        elif m.tipo == 'salida':
            for col in range(1, 10):
                ws2.cell(row=row_num, column=col).fill = amarillo_fill

    anchos2 = [22, 14, 10, 10, 8, 12, 12, 35, 16]
    for i, w in enumerate(anchos2, 1):
        ws2.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    # â•â• HOJA 3: INGREDIENTES POR PRODUCTO â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    ws3 = wb.create_sheet("Ingredientes por Producto")

    headers3 = ["Producto", "CategorÃ­a producto", "Ingrediente", "Cantidad/porciÃ³n", "Unidad", "Solicitudes pagadas", "Ingrediente rentable"]
    ws3.append(headers3)
    for col, _ in enumerate(headers3, 1):
        c = ws3.cell(row=1, column=col)
        c.fill = header_fill
        c.font = header_font
        c.alignment = center

    recetas = RecetaProducto.objects.select_related(
        'producto', 'ingrediente'
    ).filter(estado=True).order_by('producto__nombre')

    for r in recetas:
        solis = Solicitudes.objects.filter(
            producto=r.producto,
            estado__in=['pagada', 'aceptada']
        ).count()

        rentable = "âœ… SÃ­" if solis > 0 else "âŒ No â€” producto sin ventas"

        ws3.append([
            r.producto.nombre,
            r.producto.categoria,
            r.ingrediente.nombre,
            float(r.cantidad_por_porcion),
            r.ingrediente.unidad,
            solis,
            rentable,
        ])
        row_num = ws3.max_row
        fill = verde_fill if solis > 0 else rojo_fill
        for col in range(1, 8):
            ws3.cell(row=row_num, column=col).fill = fill

    anchos3 = [25, 16, 22, 14, 8, 16, 22]
    for i, w in enumerate(anchos3, 1):
        ws3.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario_decisiones.xlsx"'
    wb.save(response)
    return response


@login_requerido
def inventario_export_pdf(request):
    """
    PDF ejecutivo: resumen de ingredientes con veredicto para toma de decisiones.
    """
    from django.db.models import Sum
    from .models import Inventario, Movimiento, RecetaProducto, Solicitudes

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario_decisiones.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=landscape(A4),
        leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Reporte de Inventario â€” AnÃ¡lisis para Toma de Decisiones</b>", styles['Title']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Verde = rentable Â· Amarillo = revisar Â· Rojo = eliminar o reabastecer urgente",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))

    data = [[
        "Ingrediente", "CategorÃ­a", "Stock", "MÃ­n.",
        "Salidas", "Mermas", "% Merma",
        "Prods.", "Solicitudes", "Veredicto"
    ]]

    qs = Inventario.objects.select_related('id_proveedor').order_by('categoria', 'nombre')
    filas_colores = []

    for ing in qs:
        salidas = Movimiento.objects.filter(id_inventario=ing, tipo='salida').aggregate(t=Sum('cantidad'))['t'] or 0
        mermas  = Movimiento.objects.filter(id_inventario=ing, tipo='merma').aggregate(t=Sum('cantidad'))['t'] or 0
        total   = salidas + mermas
        pct     = round(mermas / total * 100, 1) if total > 0 else 0

        productos_count = RecetaProducto.objects.filter(
            ingrediente=ing, estado=True
        ).values('producto').distinct().count()

        solicitudes_count = Solicitudes.objects.filter(
            producto__receta__ingrediente=ing,
            estado__in=['pagada', 'aceptada']
        ).distinct().count()

        if solicitudes_count == 0 and productos_count == 0:
            veredicto = "Eliminar"
            color = colors.HexColor('#FFC7CE')
        elif pct > 40:
            veredicto = "Alta merma"
            color = colors.HexColor('#FFC7CE')
        elif ing.cantidad < ing.stock_minimo:
            veredicto = "Reabastecer"
            color = colors.HexColor('#FFEB9C')
        elif solicitudes_count > 5:
            veredicto = "Rentable"
            color = colors.HexColor('#C6EFCE')
        elif solicitudes_count > 0:
            veredicto = "En uso"
            color = colors.HexColor('#C6EFCE')
        else:
            veredicto = "Poca demanda"
            color = colors.HexColor('#FFEB9C')

        data.append([
            ing.nombre,
            ing.categoria,
            f"{ing.cantidad} {ing.unidad}",
            f"{ing.stock_minimo} {ing.unidad}",
            salidas,
            mermas,
            f"{pct}%",
            productos_count,
            solicitudes_count,
            veredicto,
        ])
        filas_colores.append(color)

    tabla = Table(data, repeatRows=1, colWidths=[90, 60, 55, 50, 45, 45, 50, 40, 60, 65])
    style = [
        ('BACKGROUND',  (0, 0), (-1, 0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.white),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0), 8),
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE',    (0, 1), (-1, -1), 7),
        ('GRID',        (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('ROWHEIGHT',   (0, 0), (-1, -1), 18),
    ]
    for i, color in enumerate(filas_colores, start=1):
        style.append(('BACKGROUND', (0, i), (-1, i), color))

    tabla.setStyle(TableStyle(style))
    elements.append(tabla)

    doc.build(elements)
    return response

def _filtrar_proveedores(request):
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    qs = Proveedores.objects.order_by('-id_proveedor')

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(empresa__icontains=q) |
            Q(correo__icontains=q)
        )
    if categoria:
        qs = qs.filter(inventario__categoria=categoria).distinct()

    return qs


@login_requerido
def proveedores_export_excel(request):
    qs = _filtrar_proveedores(request)

    if not qs.exists():
        messages.warning(request, "No hay proveedores para exportar.")
        return redirect('inventario')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Proveedores"

    header_fill = PatternFill("solid", fgColor="7a2d3e")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alig = Alignment(horizontal="center", vertical="center")

    headers = ["ID", "Nombre", "Apellido", "Empresa", "Telefono", "Correo", "Direccion"]
    ws.append(headers)
    for col_num, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alig

    for p in qs:
        ws.append([
            f"#{p.id_proveedores}",
            p.nombre,
            p.apellido,
            p.empresa,
            p.numero,
            p.correo,
            p.direccion,
        ])

    anchos = [10, 20, 20, 25, 15, 30, 30]
    for i, ancho in enumerate(anchos, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = ancho

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="proveedores.xlsx"'
    wb.save(response)
    return response


@login_requerido
def proveedores_export_pdf(request):
    qs = _filtrar_proveedores(request)

    if not qs.exists():
        messages.warning(request, "No hay proveedores para exportar.")
        return redirect('inventario')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="proveedores.pdf"'

    doc      = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20)
    styles   = getSampleStyleSheet()
    elements = [Paragraph("<b>Reporte de Proveedores</b>", styles['Title']), Spacer(1, 12)]

    data = [["ID", "Nombre", "Apellido", "Empresa", "Telefono", "Correo", "Direccion"]]
    for p in qs:
        data.append([
            f"#{p.id_proveedor}",
            p.nombre,
            p.apellido,
            p.empresa,
            p.numero,
            p.correo,
            p.direccion,
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#7a2d3e')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,0), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE',       (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fdf5f5')]),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#e0c8c8')),
        ('ROWHEIGHT',      (0,0), (-1,-1), 20),
    ]))
    elements.append(tabla)
    doc.build(elements)
    return response
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  VENDEDOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def _get_vendedor(request):
    """Helper interno: retorna el usuario vendedor de la sesiÃ³n o None."""
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

    # Solicitudes nuevas (Ãºltimas)
    solicitudes_nuevas = Solicitudes.objects.filter(
        producto__vendedor=vendedor,
        estado='pendiente',
        producto__categoria='eventos'
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
    ventas = Transacciones.objects.filter(
        solicitud__producto__vendedor=vendedor
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

    solicitudes = Solicitudes.objects.filter(
        producto__vendedor=usuario,
        estado='pendiente'
    )

    solicitudes_procesadas = Solicitudes.objects.filter(
        producto__vendedor=usuario,
        estado__in=['aceptada', 'rechazada', 'pagada']
    )
    
    return render(request, 'vendedor/solicitudes_vendedor.html', {
        'usuario': usuario,
        'solicitudes': solicitudes,
        'solicitudes_procesadas': solicitudes_procesadas,
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

    # EstadÃ­sticas
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
            imagen=request.FILES.get("imagen"),
            vendedor=usuario,
            estado_aprobacion='pendiente',
        )

    # Solo activos para cards/tabla principal
    productos = Productos.objects.filter(
        vendedor=usuario,
        estado=True
    ).order_by('-id_producto')

    estado = request.GET.get('estado')
    if estado:
        productos = productos.filter(estado_aprobacion=estado)

    paginator = Paginator(productos, 6)
    page = request.GET.get('page')
    productos_page = paginator.get_page(page)

    pendientes_con_receta = productos.filter(estado_aprobacion='pendiente').filter(receta__isnull=False).distinct()
    pendientes_sin_receta = productos.filter(estado_aprobacion='pendiente').filter(receta__isnull=True)
    aprobados  = productos.filter(estado_aprobacion='aprobado')
    rechazados = productos.filter(estado_aprobacion='rechazado')

    # Solo inhabilitados
    inhabilitados = Productos.objects.filter(vendedor=usuario, estado=False)

    return render(request, "vendedor/productos_vendedor.html", {
        "usuario": usuario,
        "productos": productos_page,
        "estado": estado,
        "pendientes_con_receta": pendientes_con_receta,
        "pendientes_sin_receta": pendientes_sin_receta,
        "aprobados": aprobados,
        "rechazados": rechazados,
        "inhabilitados": inhabilitados,  # nuevo
    })

#acciones ----------------------------------------------------------------------------------------->
#acciones ----------------------------------------------------------------------------------------->
#acciones ----------------------------------------------------------------------------------------->
#productos
@login_requerido
def cambiar_estado_producto_vendedor(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == "POST":
        try:
            producto = get_object_or_404(Productos, id_producto=id_producto)
            vendedor = producto.vendedor  # esto faltaba

            producto.estado = not producto.estado
            producto.save()

            if producto.estado_aprobacion == 'aprobado' and not producto.estado:
                PQRS.objects.create(
                    asunto='Producto inhabilitado por vendedor',
                    mensaje=f'El vendedor {vendedor.nombre} {vendedor.apellido} ha inhabilitado el producto "{producto.nombre}" (ID: {producto.id_producto}). Este producto estaba aprobado.',
                    usuario=vendedor,
                    categoria='reporte',
                    estado_respuesta='sin_respuesta'
                )
                messages.info(request, "Producto inhabilitado. Se notificÃ³ al administrador.")
            else:
                messages.success(request, "Estado del producto actualizado.")
        
        except Exception as e:
            messages.error(request, "Error al cambiar estado. Intentalo de nuevo")

    return redirect("vendedor_productos")

@login_requerido
def editar_producto_vendedor(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)

    if request.method == "POST":
        try:
            if producto.estado_aprobacion == 'aprobado':
                campos = ['nombre', 'descripcion', 'precio', 'categoria']
                mensaje = ""

                for campo in campos:
                    valor_nuevo = request.POST.get(campo)
                    valor_actual = getattr(producto, campo)

                    if valor_nuevo and str(valor_nuevo) != str(valor_actual):
                        mensaje += f"{campo}:\n"
                        mensaje += f"  Antes: {valor_actual}\n"
                        mensaje += f"  Nuevo: {valor_nuevo}\n\n"

                if request.FILES.get("imagen"):
                    mensaje += "imagen:\n  (Nueva imagen adjunta)\n\n"

                if mensaje:
                    PQRS.objects.create(
                        usuario=producto.vendedor,
                        asunto=f"Solicitud ediciÃ³n de producto #{producto.id_producto}",
                        mensaje=f"[Producto ID: {producto.id_producto}]\n\n" + mensaje,
                        categoria='solicitud',
                        estado_respuesta='sin_respuesta'
                    )
                    messages.info(request, "Solicitud enviada al administrador para revisiÃ³n.")
                else:
                    messages.warning(request, "No detectamos cambios en el producto.")

                return redirect('vendedor_productos')

            # Pendiente o rechazado â€” editar directo
            producto.nombre = request.POST.get("nombre")
            producto.descripcion = request.POST.get("descripcion")
            producto.precio = request.POST.get("precio")
            producto.categoria = request.POST.get("categoria")
            if request.FILES.get("imagen"):
                producto.imagen = request.FILES.get("imagen")

            if producto.estado_aprobacion == 'rechazado':
                producto.estado_aprobacion = 'pendiente'
                messages.success(request, "Producto reenviado a revisiÃ³n.")
            else:
                messages.success(request, "Producto actualizado correctamente.")

            producto.save()

        except Exception as e:
            messages.error(request, f"Error real: {e}")

    return redirect('vendedor_productos')

@login_requerido
def carga_masiva_productos(request):
    print("METHOD:", request.method)
    print("FILES:", request.FILES)

    if request.method == 'POST':

        vendedor = _get_vendedor(request)
        if not vendedor:
            return redirect('inicio')

        if 'csv' not in request.FILES or 'zip' not in request.FILES:
            messages.error(request, "Debes subir ambos archivos (CSV y ZIP)")
            print("No se subieron archivos")
            return redirect('vendedor_productos')

        archivo_csv = request.FILES['csv']
        archivo_zip = request.FILES['zip']

        ruta_temp = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(ruta_temp, exist_ok=True)

        productos_creados = 0

        try:
            # Descomprimir ZIP
            try:
                with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                    zip_ref.extractall(ruta_temp)
                    print("Contenido ZIP:", zip_ref.namelist())  # para ver quÃ© hay adentro
                print("ZIP descomprimido")
            except Exception as e:
                messages.error(request, "Error al leer el ZIP")
                print("Error ZIP:", e)
                return redirect('vendedor_productos')

            # Leer CSV
            try:
                archivo = TextIOWrapper(archivo_csv.file, encoding='utf-8')
                reader = csv.DictReader(archivo)
            except Exception as e:
                messages.error(request, "Error al leer el CSV")
                print("Error CSV:", e)
                return redirect('vendedor_productos')

            for fila in reader:
                print("FILA:", fila)

                try:
                    if not fila.get('nombre') or not fila.get('precio'):
                        print("Fila invÃ¡lida:", fila)
                        continue

                    producto = Productos(
                        nombre=fila['nombre'],
                        descripcion=fila.get('descripcion', ''),
                        precio=fila['precio'],
                        categoria=fila.get('categoria', 'diarios'),
                        estado_aprobacion='pendiente',
                        vendedor=vendedor
                    )

                    producto.save()

                    # Buscar imagen en toda la carpeta temp (incluyendo subcarpetas)
                    nombre_imagen = fila.get('imagen', '').strip()
                    if nombre_imagen:
                        ruta_imagen = None
                        for root, dirs, files in os.walk(ruta_temp):
                            if nombre_imagen in files:
                                ruta_imagen = os.path.join(root, nombre_imagen)
                                break

                        if ruta_imagen:
                            with open(ruta_imagen, 'rb') as f:
                                producto.imagen.save(nombre_imagen, File(f), save=True)
                            print("Imagen asignada:", nombre_imagen)
                        else:
                            print("Imagen NO encontrada:", nombre_imagen)

                    productos_creados += 1

                except Exception as e:
                    import traceback
                    print("Error en fila:", fila)
                    traceback.print_exc()
                    continue

        finally:
            shutil.rmtree(ruta_temp, ignore_errors=True)

        if productos_creados > 0:
            messages.success(request, f"Se subieron {productos_creados} productos correctamente")
        else:
            messages.warning(request, "No se creÃ³ ningÃºn producto (revisa tu CSV)")

    return redirect('vendedor_productos')

@login_requerido
def crear_productos(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')
    
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        precio = request.POST.get("precio")
        imagen = request.FILES.get("imagen")
        categoria = request.POST.get("categoria")

        # ValidaciÃ³n de campos vacÃ­os
        if not all([nombre, descripcion, precio, categoria]):
            messages.warning(request, "Todos los campos son obligatorios.")
            return redirect("vendedor_productos")

        try:
            Productos.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                imagen=imagen,
                vendedor=vendedor,
                categoria=categoria,
                estado_aprobacion='pendiente'
            )
            messages.success(request, "Â¡Producto creado! QuedarÃ¡ pendiente de aprobaciÃ³n.")

        except Exception as e:
            messages.error(request, "Error al guardar. Intentalo de nuevo")

    return redirect("vendedor_productos")

def descargar_plantilla_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantilla_productos.csv"'

    writer = csv.writer(response)
    
    # Encabezados (IMPORTANTE)
    writer.writerow(['nombre', 'descripcion', 'precio', 'categoria', 'imagen'])

    # Ejemplo (esto ayuda MUCHÃSIMO al usuario)
    writer.writerow(['Pastel de chocolate', 'Delicioso pastel', '500', 'antojos', 'pastel.jpg'])

    return response

@login_requerido
def eliminar_producto_vendedor(request, id_producto):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')
        
    producto = get_object_or_404(Productos, id_producto=id_producto, vendedor=vendedor)
    
    if request.method == 'POST':
        try:
            # Solo se pueden eliminar pendientes, rechazados e inhabilitados
            # Los aprobados no se eliminan directamente
            if producto.estado_aprobacion == 'aprobado' and producto.estado:
                messages.error(request, "No puedes eliminar un producto aprobado y activo.")
                return redirect('vendedor_productos')
            
            producto.delete()
            messages.success(request, "Producto eliminado permanentemente.")
        
        except Exception as e:
            messages.error(request, "Error al guardar. Intentalo de nuevo")
    
    return redirect('vendedor_productos')
#solicitudes ------------------------------------------------------------------------------------>
#solicitudes ------------------------------------------------------------------------------------>
#solicitudes ------------------------------------------------------------------------------------>

@login_requerido
def aceptar_soli(request, id_solicitud):
    vendedor = _get_vendedor(request)
    if not vendedor: 
        return redirect('inicio')
    
    solicitud = get_object_or_404(Solicitudes, id_solicitud=id_solicitud)

    if request.method == "POST":
        accion = request.POST.get("accion")

        try:
            if accion == "aceptar":
                porcentaje = request.POST.get("porcentaje_abono")

                if not porcentaje or not porcentaje.isdigit():
                    messages.error(request, "Debes ingresar un porcentaje vÃ¡lido para aceptar.")
                    return redirect('vendedor_solicitudes')

                porcentaje = int(porcentaje)
                if not (1 <= porcentaje <= 100):
                    messages.error(request, "El porcentaje debe estar entre 1 y 100.")
                    return redirect('vendedor_solicitudes')

                if solicitud.producto.categoria == 'eventos':
                    ok, mensajes = bajar_inventario_por_solicitud(solicitud)
                    if not ok:
                        for e in mensajes:
                            messages.error(request, e)
                        return redirect('vendedor_solicitudes')
                    for m in mensajes:  # advertencias (ej: sin receta)
                        messages.warning(request, m)

                solicitud.estado = "aceptada"
                solicitud.abono = (solicitud.precio_total * porcentaje) / 100
                solicitud.save()
                correo_estado_solicitud(solicitud)
                messages.success(request, "Solicitud aceptada correctamente.")

            elif accion == "rechazar":
                solicitud.estado = "rechazada"
                messages.info(request, "Solicitud rechazada.")

            solicitud.save()

        except Exception as e:
            messages.error(request, "OcurriÃ³ un error al procesar la solicitud.")

    return redirect('vendedor_solicitudes')

#perfil ------------------------------------------------------------------------------------------>
#perfil ------------------------------------------------------------------------------------------>
#perfil ------------------------------------------------------------------------------------------>

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

    # Clientes Ãºnicos
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
def editar_perfil_vendedor(request):
    usuario = _get_vendedor(request)
    if not usuario:
        return redirect('inicio')

    if request.method == "POST":
        try:
            datos = {
                "nombre": request.POST.get('nombre'),
                "apellido": request.POST.get('apellido'),
                "correo": request.POST.get('correo'),
                "numero": request.POST.get('numero'),
                "direccion": request.POST.get('direccion')
            }

            # Crear un mensaje legible para el admin
            mensaje = ""
            for campo, valor in datos.items():
                valor_actual = getattr(usuario, campo)

                if valor and valor != valor_actual:
                    mensaje += f"{campo}:\n"
                    mensaje += f"  Antes: {valor_actual}\n"
                    mensaje += f"  Nuevo: {valor}\n\n"

            PQRS.objects.create(
                usuario=usuario,
                asunto="Solicitud cambio de perfil",
                mensaje=mensaje,  # AquÃ­ ya no guardamos JSON crudo
                categoria='solicitud',
                estado_respuesta='sin_respuesta'
            )
            messages.info(request, "Tu solicitud de cambio de informacion ha sido enviada para futura revision.")

        except Exception as e:
            messages.error(request, "OcurriÃ³ un error al procesar la solicitud.")

    return redirect('vendedor_perfil')

#reportes--------------------------------------------------------------------------------------------->
#reportes--------------------------------------------------------------------------------------------->
#reportes--------------------------------------------------------------------------------------------->

@login_requerido
def crear_reporte_vendedor(request):
    vendedor = _get_vendedor(request)
    if not vendedor:
        return redirect('inicio')

    if request.method == "POST":
        try:
            asunto = request.POST.get('asunto')
            categoria = request.POST.get('categoria')
            mensaje = request.POST.get('mensaje')

            # Validar que no estÃ©n vacÃ­os
            if asunto and categoria and mensaje:
                PQRS.objects.create(
                    usuario=vendedor,
                    asunto=asunto,
                    mensaje=mensaje,
                    categoria=categoria,
                    estado_respuesta='sin_respuesta'
                )
                messages.success(request, "Tu PQRS ha sido enviada con exito. Espere respuesta del admin.")
            else:
                messages.warning(request, "Faltan campos por llenar.")

            return redirect('vendedor_reportes')
        except Exception as e:
            messages.error(request, "OcurriÃ³ un error generando el reporte. Intentalo de nuevo")

    pendientes = PQRS.objects.filter(
        usuario=vendedor,
        estado_respuesta='sin_respuesta'
    )

    respondidos = PQRS.objects.filter(
        usuario=vendedor,
        estado_respuesta='respondido'
    )

    return render(request, "vendedor/reportes_vendedor.html", {
        "usuario": vendedor,
        "sin_respuesta": pendientes,
        "respondidos": respondidos
    })

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  CLIENTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def perfil_cliente(request):
    usuario = get_usuario_sesion(request)

    if request.method == 'POST':

        if request.POST.get('cambiar_contrasena'):
            actual    = request.POST.get('contrasena_actual', '').strip()
            nueva     = request.POST.get('nueva_contrasena', '').strip()
            confirmar = request.POST.get('confirmar_contrasena', '').strip()

            if not all([actual, nueva, confirmar]):
                messages.warning(request, "Todos los campos de contraseÃ±a son obligatorios.")
                return redirect('perfil_cliente')

            if not check_password(actual, usuario.contrasena):
                messages.error(request, "La contraseÃ±a actual es incorrecta.")
                return redirect('perfil_cliente')

            if nueva != confirmar:
                messages.error(request, "La nueva contraseÃ±a y la confirmaciÃ³n no coinciden.")
                return redirect('perfil_cliente')

            if len(nueva) < 6:
                messages.warning(request, "La nueva contraseÃ±a debe tener al menos 6 caracteres.")
                return redirect('perfil_cliente')

            usuario.contrasena = make_password(nueva)
            usuario.save()
            messages.success(request, "ContraseÃ±a actualizada correctamente.")

        else:
            nombre   = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            correo   = request.POST.get('correo', '').strip()
            numero   = request.POST.get('numero', '').strip()

            if not all([nombre, apellido, correo, numero]):
                messages.warning(request, "Los campos nombre, apellido, correo y nÃºmero son obligatorios.")
                return redirect('perfil_cliente')

            if Usuarios.objects.filter(correo=correo).exclude(id_usuario=usuario.id_usuario).exists():
                messages.error(request, "Este correo ya estÃ¡ registrado por otro usuario.")
                return redirect('perfil_cliente')

            try:
                usuario.nombre    = nombre
                usuario.apellido  = apellido
                usuario.correo    = correo
                usuario.numero    = numero
                usuario.direccion = request.POST.get('direccion', usuario.direccion)
                usuario.save()
                request.session['usuario_nombre'] = usuario.nombre
                messages.success(request, "Perfil actualizado correctamente.")
            except Exception:
                messages.error(request, "OcurriÃ³ un error al actualizar el perfil. Intenta de nuevo.")

        return redirect('perfil_cliente')

    total_pedidos         = Solicitudes.objects.filter(usuario=usuario).count()
    total_gastado         = Solicitudes.objects.filter(usuario=usuario).aggregate(t=Sum('precio_total'))['t'] or 0
    total_pqrs            = PQRS.objects.filter(usuario=usuario).count()
    solicitudes_recientes = Solicitudes.objects.filter(usuario=usuario).order_by('-fecha_creacion')[:4]

    return render(request, 'cliente/perfil_cliente.html', {
        'usuario':               usuario,
        'total_pedidos':         total_pedidos,
        'total_gastado':         total_gastado,
        'total_pqrs':            total_pqrs,
        'solicitudes_recientes': solicitudes_recientes,
    })

def catalogo(request):
    if request.GET.get('cancelado'):
        messages.warning(request, "Compra cancelada. Puedes seguir explorando el catÃ¡logo.")
    usuario = get_usuario_sesion(request)
    categoria = request.GET.get("categoria", "todos")
    pasteles = (
        Productos.objects.filter(categoria=categoria, estado=True, estado_aprobacion='aprobado')
        if categoria != "todos"
        else Productos.objects.filter(estado=True, estado_aprobacion='aprobado')
    )
    return render(request, "cliente/catalogo.html", {
        "pasteles": pasteles,
        "categoria_activa": categoria,
        "total": pasteles.count(),
        "usuario": usuario,
    })


def compra_rapida(request, producto_id):
    producto = get_object_or_404(Productos, id_producto=producto_id, estado_aprobacion='aprobado', estado=True)
    usuario_id = request.session.get('usuario_id')
    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'cliente/compra_rapida.html', {
        'producto': producto,
        'usuario': usuario,
    })


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  TRANSACIIONES DEL CLIENTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@login_requerido
def mis_transacciones(request):
    usuario = get_usuario_sesion(request)

    transacciones = Transacciones.objects.filter(
        solicitud__usuario=usuario
    ).select_related('solicitud__producto').order_by('-fecha_creacion')

    total_pagado = transacciones.aggregate(total=Sum('importe_total'))['total'] or 0
    total_tx     = transacciones.count()
    terminadas   = transacciones.filter(estado='terminado').count()
    abonadas     = transacciones.filter(estado='abonado').count()

    return render(request, 'cliente/mis_transacciones.html', {
        'usuario':       usuario,
        'transacciones': transacciones,
        'total_pagado':  total_pagado,
        'total_tx':      total_tx,
        'terminadas':    terminadas,
        'abonadas':      abonadas,
    })

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  CONFIGURADOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def configurador(request, producto_id):
    producto = get_object_or_404(
        Productos, id_producto=producto_id,
        estado_aprobacion='aprobado', estado=True
    )
    usuario_id = request.session.get('usuario_id')

    if producto.categoria == 'eventos' and not usuario_id:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None
    return render(request, 'cliente/configurador.html', {
        'producto':   producto,
        'usuario':    usuario,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
    })


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  SOLICITUDES (CLIENTE)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def crear_solicitud(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo')

    producto   = get_object_or_404(Productos, id_producto=producto_id)
    usuario_id = request.session.get('usuario_id')
    usuario    = Usuarios.objects.get(id_usuario=usuario_id) if usuario_id else None

    if producto.categoria == 'eventos' and not usuario:
        messages.warning(request, "Debes iniciar sesiÃ³n para solicitar un evento.")
        return redirect('inicio')

    precio_total = int(float(request.POST.get('precio_total', producto.precio)))

    try:
        solicitud = Solicitudes.objects.create(
            usuario           = usuario,
            producto          = producto,
            nombre_invitado   = request.POST.get('nombre_invitado', ''),
            correo_invitado   = request.POST.get('correo_invitado', ''),
            direccion_entrega = request.POST.get('direccion_entrega', ''),
            tipo_entrega      = request.POST.get('tipo_entrega', 'tienda'),
            mensaje_pastel    = request.POST.get('mensaje_pastel', ''),
            cobertura         = request.POST.get('cobertura', ''),
            rellenos          = request.POST.get('rellenos', ''),
            decoracion        = request.POST.get('decoracion', ''),
            pisos             = int(request.POST.get('pisos', 1)),
            porciones         = request.POST.get('porciones') or None,
            precio_total      = precio_total,
            abono             = 0,
            descripcion       = request.POST.get('descripcion_config', ''),
            fecha_evento      = request.POST.get('fecha_evento') or None,
            estado            = 'pendiente',
        )
    except Exception as e:
        messages.error(request, "OcurriÃ³ un error al crear la solicitud. Intenta de nuevo.")
        return redirect('catalogo')

    if producto.categoria == 'eventos':
        messages.success(request, "Â¡Solicitud enviada! Pronto nos pondremos en contacto contigo.")
        return redirect('solicitud_pendiente', solicitud_id=solicitud.id_solicitud)

    return _redirigir_a_mercadopago(solicitud, usuario, producto, precio_total)

@login_requerido
def mis_solicitudes(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('inicio')
    usuario = get_usuario_sesion(request)
    estado = request.GET.get('estado', 'todos')
    solicitudes = Solicitudes.objects.filter(usuario_id=usuario_id).order_by('-fecha_creacion')
    if estado != 'todos':
        solicitudes = solicitudes.filter(estado=estado)

    return render(request, 'cliente/mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'estado_activo': estado,
        'usuario': usuario,
    })

@login_requerido
def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    usuario = get_usuario_sesion(request)
    return render(request, 'cliente/detalle_solicitud.html', {
        'solicitud': solicitud,
        'usuario': usuario,
    })


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
    usuario = get_usuario_sesion(request)  
    return render(request, 'cliente/solicitud_pendiente.html', {
        'solicitud': solicitud,
        'usuario': usuario, 
    })


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PQRS CLIENTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@login_requerido
def mis_pqrs(request):
    usuario = get_usuario_sesion(request)

    filtro_activo = request.GET.get('f', 'todos')
    qs = PQRS.objects.filter(usuario=usuario)

    if filtro_activo == 'sin_respuesta':
        qs = qs.filter(estado_respuesta='sin_respuesta')
    elif filtro_activo == 'respondido':
        qs = qs.filter(estado_respuesta='respondido')
    elif filtro_activo in ['pregunta', 'queja', 'reporte', 'solicitud']:
        qs = qs.filter(categoria=filtro_activo)

    return render(request, 'cliente/mis_pqrs.html', {
        'usuario':       usuario,
        'pqrs_list':     qs.order_by('-id_pqrs'),
        'filtro_activo': filtro_activo,
    })


@login_requerido
def crear_pqrs(request):
    usuario = get_usuario_sesion(request)

    if request.method != 'POST':
        return redirect('mis_pqrs')

    asunto    = request.POST.get('asunto', '').strip()
    mensaje   = request.POST.get('mensaje', '').strip()
    categoria = request.POST.get('categoria', '').strip()

    if not all([asunto, mensaje, categoria]):
        messages.warning(request, "Todos los campos son obligatorios.")
        return redirect('mis_pqrs')

    try:
        PQRS.objects.create(
            usuario          = usuario,
            asunto           = asunto,
            mensaje          = mensaje,
            categoria        = categoria,
            estado_respuesta = 'sin_respuesta',
        )
        messages.success(request, "Â¡Tu PQRS fue enviada correctamente! Te responderemos pronto.")
    except Exception:
        messages.error(request, "OcurriÃ³ un error al enviar tu PQRS. Intenta de nuevo.")

    return redirect('mis_pqrs')
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  MERCADOPAGO â€” PAGOS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

    return redirect(preference["response"]["sandbox_init_point"])


@login_requerido
def pagar_abono(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('inicio')

    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"Abono â€” {solicitud.producto.nombre}",
            "quantity": 1,
            "unit_price": int(solicitud.abono),
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
    print("=== RESPUESTA MERCADOPAGO ===")
    print(preference)
    print("==============================")

    response = preference.get("response", {})
    init_point = response.get("sandbox_init_point") or response.get("init_point")

    if not init_point:
        return HttpResponse(
            f"Error al crear preferencia de pago. Respuesta de MercadoPago: {response}",
            status=500
        )

    return redirect(init_point)

def pago_exitoso(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    solicitud.estado = 'pagada'
    solicitud.save()
    usuario = get_usuario_sesion(request)  # â† agrega esto
    return render(request, 'cliente/pago_exitoso.html', {
        'solicitud': solicitud,
        'usuario': usuario,  # â† agrega esto
    })

def pago_fallido(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    usuario = get_usuario_sesion(request)  
    return render(request, 'cliente/pago_fallido.html', {
        'solicitud': solicitud,
        'usuario': usuario, 
    })

def pago_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(Solicitudes, id_solicitud=solicitud_id)
    usuario = get_usuario_sesion(request)  
    return render(request, 'cliente/pago_pendiente.html', {
        'solicitud': solicitud,
        'usuario': usuario,  
    })

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  MERCADOPAGO â€” WEBHOOK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  COMPRAS DE INVITADO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def mis_compras_invitado(request):
    correo  = request.GET.get('correo', '').strip()
    usuario = get_usuario_sesion(request)
    solicitudes = Solicitudes.objects.none()  # â† queryset vacÃ­o, no lista

    if usuario:
        solicitudes = Solicitudes.objects.filter(
            usuario=usuario
        ).select_related('producto').order_by('-fecha_creacion')
    elif correo:
        solicitudes = Solicitudes.objects.filter(
            correo_invitado=correo,
            usuario=None
        ).select_related('producto').order_by('-fecha_creacion')

    # Ahora sÃ­ es un queryset y puedes usar .filter() y .aggregate()
    total_gastado = solicitudes.filter(estado='pagada').aggregate(
        total=Sum('precio_total')
    )['total'] or 0

    pendientes_count = solicitudes.filter(estado__in=['pendiente', 'aceptada']).count()

    return render(request, 'cliente/mis_compras_invitado.html', {
        'solicitudes':      solicitudes,
        'correo':           correo,
        'usuario':          usuario,
        'total_gastado':    total_gastado,
        'pendientes_count': pendientes_count,
    })


# =======================================================================================
# INVENTARIO
# =======================================================================================

@login_requerido
def gestionar_receta(request, id_producto):
    vendedor = _get_vendedor(request)
    producto = get_object_or_404(Productos, id_producto=id_producto, vendedor=vendedor)

    if producto.categoria != 'eventos':
        return redirect('vendedor_productos')

    ingredientes_disponibles = Inventario.objects.filter(estado=True)
    receta_actual = RecetaProducto.objects.filter(producto=producto, estado=True)

    if request.method == 'POST':
        RecetaProducto.objects.filter(producto=producto).delete()

        ingredientes = request.POST.getlist('ingrediente')
        cantidades = request.POST.getlist('cantidad_por_porcion')

        for ing_id, cantidad in zip(ingredientes, cantidades):
            if ing_id and cantidad:
                RecetaProducto.objects.create(
                    producto=producto,
                    ingrediente_id=ing_id,
                    cantidad_por_porcion=cantidad
                )

        messages.success(request, "Receta actualizada correctamente.")
        return redirect('vendedor_productos')

    return render(request, 'vendedor/gestionar_receta.html', {
        'producto': producto,
        'ingredientes_disponibles': ingredientes_disponibles,
        'receta_actual': receta_actual,
    })


def bajar_inventario_por_solicitud(solicitud):
    porciones = solicitud.porciones or 1
    receta = RecetaProducto.objects.filter(
        producto=solicitud.producto,
        estado=True
    ).select_related('ingrediente')

    if not receta.exists():
        return True, ["El producto no tiene receta cargada, no se descontÃ³ inventario."]

    errores = []
    for item in receta:
        cantidad_necesaria = item.cantidad_por_porcion * porciones
        if item.ingrediente.cantidad < cantidad_necesaria:
            errores.append(
                f"Stock insuficiente de '{item.ingrediente.nombre}': "
                f"necesitas {cantidad_necesaria} {item.ingrediente.unidad}, "
                f"hay {item.ingrediente.cantidad}."
            )

    if errores:
        return False, errores

    for item in receta:
        cantidad_necesaria = item.cantidad_por_porcion * porciones
        ingrediente = item.ingrediente
        ingrediente.cantidad -= int(cantidad_necesaria)
        ingrediente.save()

        Movimiento.objects.create(
            id_inventario=ingrediente,
            cantidad=int(cantidad_necesaria),
            tipo='salida',
            observacion=f'Solicitud #{solicitud.id_solicitud} â€” {solicitud.producto.nombre} ({porciones} porciones)'
        )

    return True, []

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  CORREOS MASIVOS â€” EmailJS via HTTP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def _enviar_emailjs(to_email, subject, username, message, subtitle="NotificaciÃ³n del sistema",
                    button_text="", button_link=""):
    """
    FunciÃ³n base que llama a la API HTTP de EmailJS.
    Retorna True si el correo se enviÃ³, False si fallÃ³.
    """
    try:
        response = requests.post(
            'https://api.emailjs.com/api/v1.0/email/send',
            json={
                'service_id':  settings.EMAILJS_SERVICE_ID,
                'template_id': settings.EMAILJS_TEMPLATE_ID,
                'user_id':     settings.EMAILJS_PUBLIC_KEY,
                'accessToken': settings.EMAILJS_PRIVATE_KEY,
                'template_params': {
                'to_email': to_email,
                'subject': subject,
                'username': username,
                'message': message,
                'subtitle': subtitle,
                'button_text': button_text,
                'button_link': button_link,
            },
            },
            timeout=10,
        )
        if response.status_code == 200:
            print(f"[EMAILJS OK] â†’ {to_email}")
            return True
        else:
            print(f"[EMAILJS ERROR {response.status_code}] {response.text}")
            return False
    except Exception as e:
        print(f"[EMAILJS EXCEPTION] {e}")
        return False


# â”€â”€ ACTIVACIÃ“N DE CUENTA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def correo_activacion(usuario, request):
    enlace = f"{request.scheme}://{request.get_host()}/activar/{usuario.token_activacion}/"
    _enviar_emailjs(
        to_email=usuario.correo,
        subject='Activa tu cuenta en CreartSoft',
        username=usuario.nombre,
        message=(
            f"Gracias por registrarte en CreartSoft.\n\n"
            f"Haz clic en el siguiente enlace para activar tu cuenta:\n\n"
            f"{enlace}\n\n"
            f"Si no te registraste, ignora este correo."
        ),
    )

def activar_cuenta(request, token):
    try:
        usuario = Usuarios.objects.get(token_activacion=token)

        usuario.estado = True
        usuario.token_activacion = ''
        usuario.save()

        messages.success(
            request,
            "Tu cuenta fue activada correctamente."
        )

    except Usuarios.DoesNotExist:
        messages.error(
            request,
            "El enlace de activaciÃ³n no es vÃ¡lido."
        )

    return redirect('inicio')

# â”€â”€ RECUPERACIÃ“N DE CONTRASEÃ‘A â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def correo_recuperacion(usuario, token, request):
    enlace = f"{request.scheme}://{request.get_host()}/nueva-contrasena/{token}/"
    _enviar_emailjs(
        to_email=usuario.correo,
        subject='Recupera tu contraseÃ±a - CreartSoft',
        username=usuario.nombre,
        message=(
            f"Recibimos una solicitud para cambiar tu contraseÃ±a.\n\n"
            f"Haz clic aquÃ­ para crear una nueva:\n\n"
            f"{enlace}\n\n"
            f"Este enlace expira en 1 hora. Si no lo pediste, ignora este correo."
        ),
    )


# â”€â”€ ESTADO DE SOLICITUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def correo_estado_solicitud(solicitud):
    """
    llamar despuÃ©s de solicitud.save() en aceptar_soli() y donde cambies estados.
    """
    if not solicitud.usuario:
        return  # invitado sin correo registrado

    estados = {
        'aceptada': (
            'âœ… Tu solicitud fue aceptada - CreartSoft',
            f'Â¡Buenas noticias! Tu pedido de "{solicitud.producto.nombre}" fue aceptado.\n'
            f'El abono a pagar es ${solicitud.abono}.\n\n'
            f'Ingresa a tu cuenta para ver el detalle y realizar el pago.'
        ),
        'rechazada': (
            'âŒ Tu solicitud fue rechazada - CreartSoft',
            f'Lamentamos informarte que tu pedido de "{solicitud.producto.nombre}" '
            f'no pudo ser aceptado en este momento.\n\n'
            f'Si tienes dudas, puedes contactarnos por PQRS.'
        ),
        'pagada': (
            'ðŸ’³ Pago confirmado - CreartSoft',
            f'Confirmamos el pago de tu pedido "{solicitud.producto.nombre}".\n\n'
            f'Â¡Nos ponemos a trabajar! Gracias por confiar en CreartSoft.'
        ),
    }

    if solicitud.estado not in estados:
        return

    subject, message = estados[solicitud.estado]
    _enviar_emailjs(
        to_email=solicitud.usuario.correo,
        subject=subject,
        username=solicitud.usuario.nombre,
        message=message,
    )


# â”€â”€ RESPUESTA A PQRS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def correo_respuesta_pqrs(pqrs):
    """
    llamar despuÃ©s de pqrs_obj.save() en pqrs_responder().
    """
    _enviar_emailjs(
        to_email=pqrs.usuario.correo,
        subject='Te respondieron tu PQRS - CreartSoft',
        username=pqrs.usuario.nombre,
        message=(
            f'Tu {pqrs.categoria} sobre "{pqrs.asunto}" ha sido respondida:\n\n'
            f'{pqrs.respuesta}\n\n'
            f'Puedes ver el detalle completo en tu perfil.'
        ),
    )

# â”€â”€ VALIDACION DE CONTRASENAS IGUALES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def nueva_contrasena(request, token):
    print("TOKEN RECIBIDO:", token)
    usuario = get_object_or_404(Usuarios, token_activacion=token)
    
    if request.method == 'POST':
        contrasena  = request.POST.get('contrasena', '').strip()
        contrasena2 = request.POST.get('contrasena2', '').strip()

        if contrasena != contrasena2:
            messages.error(request, "Las contraseÃ±as no coinciden.")
            return render(request, 'nueva_contrasena.html', {'token': token})

        usuario.contrasena = make_password(contrasena)
        usuario.token_activacion = ''
        usuario.save()
        messages.success(request, "ContraseÃ±a actualizada. Ya puedes iniciar sesiÃ³n.")
        return redirect('inicio')
    
    return render(request, 'nueva_contrasena.html', {'token': token})

# â”€â”€ RECUPERACION DE CONTRASEÃ‘A CON ESTADO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def recuperacion_contrasena(request):
    if request.method != 'POST':
        return render(request, 'recuperar_contrasena.html')
    
    correo = request.POST.get('correo', '').strip()
    try:
        usuario = Usuarios.objects.get(correo=correo, estado=True)
        token = get_random_string(64)
        usuario.token_activacion = token
        usuario.save()
        print("TOKEN GENERADO:", token)
        correo_recuperacion(usuario, token, request)
        messages.success(request, "Te enviamos un enlace a tu correo.")
    except Usuarios.DoesNotExist:
        messages.error(request, "No encontramos ese correo o la cuenta estÃ¡ inactiva.")
    return redirect('inicio')

