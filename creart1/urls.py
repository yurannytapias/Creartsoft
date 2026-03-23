"""
URL configuration for creart1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from creart import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),

    #registrar, iniciar y cerrar sesion BACKEND ------------------------------------------
    #registrar, iniciar y cerrar sesion BACKEND ------------------------------------------
    #registrar, iniciar y cerrar sesion BACKEND ------------------------------------------

    path('registro/', views.registrar_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    path('registro_vendedor/', views.registrar_vendedor, name='registro_vendedor'),

    #admin -----------------------------------------------------------------------
    #admin -----------------------------------------------------------------------
    #admin -----------------------------------------------------------------------
    path('administrador/', views.administrador, name='administrador'),


    path('vendedor/', views.vendedor, name='vendedor'),
    path('vendedor_solicitudes/', views.solicitudes_vendedor, name='vendedor_solicitudes'),
    path('vendedor_ventas/', views.ventas_vendedor, name='vendedor_ventas'),
    path('vendedor_clientes/', views.clientes_vendedor, name='vendedor_clientes'),
    path('vendedor_productos/', views.productos_vendedor, name='vendedor_productos'),
    path('vendedor_bonos/', views.bonos_vendedor, name='vendedor_bonos'),
    path('vendedor_perfil/', views.mi_perfil_vendedor, name='vendedor_perfil'),
    path('vendedor_reportes/', views.reportes_vendedor, name='vendedor_reportes'),
    path('vendedor_solicitud/', views.soli_vendedor, name='vendedor_solicitud'),
    path('crear_solicitud_vededor/', views.crear_solicitud_vededor, name='crear_solicitud_vededor'),
    path('crear_productos/', views.crear_productos, name='crear_producto'),
    path('editar_perfil/', views.editar_perfil_vendedor, name='editar_perfil_vendedor'),
    path('crear_reporte/', views.crear_reporte_vendedor, name='crear_reporte'),

    #cliente --------------------------------------------------------------------------
    #cliente --------------------------------------------------------------------------
    #cliente --------------------------------------------------------------------------

        path('catalogo/', views.catalogo, name='catalogo'),
    path('compra/<int:producto_id>/', views.compra_rapida, name='compra_rapida'),
    path('configurador/<int:producto_id>/', views.configurador, name='configurador'),
    
    # ─────────────────────────────────────────
    # SOLICITUDES (CLIENTE)
    # ─────────────────────────────────────────
    path('solicitud/<int:producto_id>/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitud/pendiente/<int:solicitud_id>/', views.solicitud_pendiente, name='solicitud_pendiente'),
    path('solicitud/detalle/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitud/cancelar/<int:solicitud_id>/', views.cancelar_solicitud, name='cancelar_solicitud'),
    path('solicitud/pagar-abono/<int:solicitud_id>/', views.pagar_abono, name='pagar_abono'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),

    # ─────────────────────────────────────────
    # MERCADOPAGO
    # ─────────────────────────────────────────
    path('webhook/mp/', views.webhook_mp, name='webhook_mp'),
    path('pago/exitoso/<int:solicitud_id>/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/<int:solicitud_id>/', views.pago_fallido, name='pago_fallido'),
    path('pago/pendiente/<int:solicitud_id>/', views.pago_pendiente, name='pago_pendiente'),
]
