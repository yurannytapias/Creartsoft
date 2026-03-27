from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from creart import views

urlpatterns = [

    # ═══════════════════════════════════════════════════════════════════
    # DJANGO ADMIN
    # ═══════════════════════════════════════════════════════════════════
    path('admin/', admin.site.urls),

    # ═══════════════════════════════════════════════════════════════════
    # PÁGINAS GENERALES
    # ═══════════════════════════════════════════════════════════════════
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),

    # ═══════════════════════════════════════════════════════════════════
    # AUTH
    # ═══════════════════════════════════════════════════════════════════
    path('login/', views.login_usuario, name='login'),
    path('registro/', views.registrar_usuario, name='registro'),
    path('registro_vendedor/', views.registrar_vendedor, name='registro_vendedor'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # ═══════════════════════════════════════════════════════════════════
    # ADMINISTRADOR
    # ═══════════════════════════════════════════════════════════════════
    path('administrador/', views.administrador, name='administrador'),
    path('administrador/usuarios/', views.usuarios, name='usuarios'),
    path('administrador/transacciones/', views.transacciones, name='transacciones'),
    path('administrador/productos/', views.productos, name='productos'),
    path('administrador/solicitudes/', views.solicitudes, name='solicitudes'),
    path('administrador/pqrs/', views.pqrs, name='pqrs'),
    path('administrador/pqrs/responder/<int:pk>/', views.pqrs_responder, name='pqrs_responder'),
    path('administrador/perfil/', views.administrador_perfil, name='administrador_perfil'),

    #acciones -------->
    #acciones -------->

    path('producto/<int:id_producto>/estado/', views.cambiar_estado_producto, name='cambiar_estado_producto'),

    # ═══════════════════════════════════════════════════════════════════
    # CLIENTE
    # ═══════════════════════════════════════════════════════════════════
    path('catalogo/', views.catalogo, name='catalogo'),
    path('compra/<int:producto_id>/', views.compra_rapida, name='compra_rapida'),
    path('configurador/<int:producto_id>/', views.configurador, name='configurador'),

    # ═══════════════════════════════════════════════════════════════════
    # SOLICITUDES (CLIENTE)
    # ═══════════════════════════════════════════════════════════════════
    path('solicitud/<int:producto_id>/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitud/pendiente/<int:solicitud_id>/', views.solicitud_pendiente, name='solicitud_pendiente'),
    path('solicitud/detalle/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitud/cancelar/<int:solicitud_id>/', views.cancelar_solicitud, name='cancelar_solicitud'),
    path('solicitud/pagar-abono/<int:solicitud_id>/', views.pagar_abono, name='pagar_abono'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),

    # ═══════════════════════════════════════════════════════════════════
    # MERCADOPAGO
    # ═══════════════════════════════════════════════════════════════════
    path('webhook/mp/', views.webhook_mp, name='webhook_mp'),
    path('pago/exitoso/<int:solicitud_id>/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/<int:solicitud_id>/', views.pago_fallido, name='pago_fallido'),
    path('pago/pendiente/<int:solicitud_id>/', views.pago_pendiente, name='pago_pendiente'),

    # ═══════════════════════════════════════════════════════════════════
    # VENDEDOR
    # ═══════════════════════════════════════════════════════════════════
    path('vendedor/', views.vendedor, name='vendedor'),
    path('vendedor/solicitudes/', views.solicitudes_vendedor, name='vendedor_solicitudes'),
    path('vendedor/solicitud/crear/', views.soli_vendedor, name='vendedor_solicitud'),
    path('vendedor/solicitud/guardar/', views.crear_solicitud_vendedor, name='crear_solicitud_vendedor'),
    path('vendedor/ventas/', views.ventas_vendedor, name='vendedor_ventas'),
    path('vendedor/clientes/', views.clientes_vendedor, name='vendedor_clientes'),
    path('vendedor/productos/', views.productos_vendedor, name='vendedor_productos'),
    path('vendedor/bonos/', views.bonos_vendedor, name='vendedor_bonos'),
    path('vendedor/perfil/', views.mi_perfil_vendedor, name='vendedor_perfil'),
    path('vendedor/perfil/editar/', views.editar_perfil_vendedor, name='editar_perfil_vendedor'),
    path('vendedor/reportes/', views.reportes_vendedor, name='vendedor_reportes'),
    

    #acciones --------------------------------------------------------
    path('vendedor/productos/crear/', views.crear_productos, name='crear_producto'),
    path('vendedor/productos/<int:id_producto>/editar/', views.editar_producto_vendedor, name='editar_producto_vendedor'),
    path('vendedor/reportes/crear/', views.crear_reporte_vendedor, name='crear_reporte_vendedor'),
    path('vendedor/producto/<int:id_producto>/estado/', views.cambiar_estado_producto_vendedor, name='cambiar_estado_producto_vendedor'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)