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
    path('recuperacion_contrasena/', views.recuperar_contrasena, name='recuperacion_contrasena'),

    # ═══════════════════════════════════════════════════════════════════
    # AUTH
    # ═══════════════════════════════════════════════════════════════════
    path('login/', views.login_usuario, name='login'),
    path('registro/', views.registrar_usuario, name='registro'),
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
    path('administrador/perfil/', views.administrador_perfil, name='administrador_perfil'),

    #exportaciones 
    path('administrador/solicitudes/exportar/excel/', views.solicitudes_export_excel, name='solicitudes_export_excel'),
    path('administrador/solicitudes/exportar/pdf/',   views.solicitudes_export_pdf,   name='solicitudes_export_pdf'),
    # ADMIN — usuarios
    path('administrador/usuarios/exportar/excel/', views.usuarios_export_excel, name='usuarios_export_excel'),
    path('administrador/usuarios/exportar/pdf/',   views.usuarios_export_pdf,   name='usuarios_export_pdf'),
    # ADMIN — transacciones
    path('administrador/transacciones/exportar/excel/', views.transacciones_export_excel, name='transacciones_export_excel'),
    path('administrador/transacciones/exportar/pdf/',   views.transacciones_export_pdf,   name='transacciones_export_pdf'),
    #ADMIN -- productos 
    path('administrador/productos/exportar/excel/', views.productos_export_excel, name='productos_export_excel'),
    path('administrador/productos/exportar/pdf/',   views.productos_export_pdf,   name='productos_export_pdf'),
    #ADMIN -- pqrs
    path('administrador/pqrs/exportar/excel/', views.pqrs_export_excel, name='pqrs_export_excel'),
    path('administrador/pqrs/exportar/pdf/',   views.pqrs_export_pdf,   name='pqrs_export_pdf'),
    #ADMIN -- Inventario
    path('administrador/inventario/',   views.inventario_admin,   name='inventario'),
    path('administrador/inventario/exportar/excel/', views.inventario_export_excel, name='inventario_export_excel'),
    path('administrador/inventario/exportar/pdf/',   views.inventario_export_pdf,   name='inventario_export_pdf'),
    #ADMIN -- proveedores
    path('administrador/proveedores/exportar/excel/', views.proveedores_export_excel, name='proveedores_export_excel'),
    path('administrador/proveedores/exportar/pdf/',   views.proveedores_export_pdf,   name='proveedores_export_pdf'),
    
    #acciones -------->
    #acciones -------->
    path('administrador/modificar_producto_inventario/<int:id_inventario>/', views.modificar_producto_inventario, name='modificar_producto_inventario'),
    path('administrador/inhactivar_elemento_inventario/<int:id_inventario>/', views.inhactivar_elemento_inventario, name='inhactivar_elemento_inventario'),
    path('administrador/modificar_proveedor/<int:id_proveedor>/', views.modificar_proveedor, name='modificar_proveedor'),
    path('administrador/inhactivar_proveedor/<int:id_proveedor>/', views.inhactivar_proveedor, name='inhactivar_proveedor'),
    path('gestionar-edicion-producto/<int:id_pqrs>/', views.gestionar_edicion_producto, name='gestionar_edicion_producto'),
    path('pqrs/responder/', views.pqrs_responder, name='pqrs_responder'),
    path('producto/<int:id_producto>/estado/', views.cambiar_estado_producto, name='cambiar_estado_producto'),
    path('gestionar-cambio-perfil/<int:id_pqrs>/', views.gestionar_cambio_perfil, name='gestionar_cambio_perfil'),   
    path('administrador/inventario/crear_elemento',   views.crear_elemento_inventario,   name='crear_elemento_inventario'),
    path('administrador/inventario/crear_proveedor',   views.crear_proveedor,   name='crear_proveedor'),
    
    # ═══════════════════════════════════════════════════════════════════
    # CLIENTE
    # ═══════════════════════════════════════════════════════════════════
    path('catalogo/', views.catalogo, name='catalogo'),
    path('compra/<int:producto_id>/', views.compra_rapida, name='compra_rapida'),
    path('configurador/<int:producto_id>/', views.configurador, name='configurador'),
    path('mis-transacciones/', views.mis_transacciones, name='mis_transacciones'),
    path('mis-pqrs/', views.mis_pqrs, name='mis_pqrs'),
    path('mis-pqrs/crear/', views.crear_pqrs, name='crear_pqrs'),
    path('mis-compras/', views.mis_compras_invitado, name='mis_compras_invitado'),
    path('mi-perfil/', views.perfil_cliente, name='perfil_cliente'),

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
    path('vendedor/ventas/', views.ventas_vendedor, name='vendedor_ventas'),
    path('vendedor/clientes/', views.clientes_vendedor, name='vendedor_clientes'),
    path('vendedor/productos/', views.productos_vendedor, name='vendedor_productos'),
    path('vendedor/perfil/', views.mi_perfil_vendedor, name='vendedor_perfil'),
    path('vendedor/perfil/editar/', views.editar_perfil_vendedor, name='editar_perfil_vendedor'),
    path('vendedor/reportes/', views.reportes_vendedor, name='vendedor_reportes'),
    
    #acciones ----------------------------------------------------------------------->
    #acciones ----------------------------------------------------------------------->
    #acciones ----------------------------------------------------------------------->
    
    path('vendedor/reportes/crear/', views.crear_reporte_vendedor, name='crear_reporte_vendedor'),
    path('vendedor/producto/<int:id_producto>/estado/', views.cambiar_estado_producto_vendedor, name='cambiar_estado_producto_vendedor'),
    path('solicitud/estado/<int:id_solicitud>/', views.aceptar_soli, name='aceptar_soli'),
    path('vendedor/productos/crear/', views.crear_productos, name='crear_producto'),
    path('vendedor/productos/crear_carga_masiva/', views.carga_masiva_productos, name='carga_masiva_productos'),
    path('vendedor/productos/descargar_plantilla/', views.descargar_plantilla_csv, name='descargar_plantilla_csv'),
    path('vendedor/productos/<int:id_producto>/editar/', views.editar_producto_vendedor, name='editar_producto_vendedor'),
    path('vendedor/producto/<int:id_producto>/eliminar/', views.eliminar_producto_vendedor, name='eliminar_producto_vendedor'),
    path('vendedor/productos/<int:id_producto>/receta/', views.gestionar_receta, name='gestionar_receta'),
    
    # ═══════════════════════════════════════════════════════════════════
    # RECUPERACIÓN DE CONTRASEÑA
    # ═══════════════════════════════════════════════════════════════════
    
    path('activar/<str:token>/', views.activar_cuenta, name='activar_cuenta'),
    
    # ═══════════════════════════════════════════════════════════════════
    # CORREOS MASIVOS -- AUTH__PASSWORD_VALIDATORS
    # ═══════════════════════════════════════════════════════════════════

    path('recuperar/', views.recuperar_contrasena, name='recuperar_contrasena'),
    
    # ═══════════════════════════════════════════════════════════════════
    # RECUPERACIÓN DE CONTRASEÑA
    # ═══════════════════════════════════════════════════════════════════
    path('recuperacion/', views.recuperacion_contrasena, name='recuperacion_contrasena'),
    path('nueva-contrasena/<str:token>/', views.nueva_contrasena, name='nueva_contrasena'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)