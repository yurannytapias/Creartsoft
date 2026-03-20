from django.contrib import admin
from django.urls import path
from creart2 import views
from django.conf import settings
from django.conf.urls.static import static

 

from django.urls import path
from creart2 import views

urlpatterns = [
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.login_usuario, name='login'),
    path('register/', views.register_usuario, name='register'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('administrador/', views.administrador, name='administrador'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Configurador y solicitudes
    path('configurador/<int:producto_id>/', views.configurador, name='configurador'),
    path('solicitud/<int:producto_id>/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitud/pendiente/<int:solicitud_id>/', views.solicitud_pendiente, name='solicitud_pendiente'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),

    # Retorno MercadoPago
    path('pago/exitoso/<int:solicitud_id>/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/<int:solicitud_id>/', views.pago_fallido, name='pago_fallido'),
    path('pago/pendiente/<int:solicitud_id>/', views.pago_pendiente, name='pago_pendiente'),
    path('solicitud/detalle/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
path('solicitud/cancelar/<int:solicitud_id>/', views.cancelar_solicitud, name='cancelar_solicitud'),
path('solicitud/pagar-abono/<int:solicitud_id>/', views.pagar_abono, name='pagar_abono'),
path('compra/<int:producto_id>/', views.compra_rapida, name='compra_rapida'),

    # Webhook
    path('webhook/mp/', views.webhook_mp, name='webhook_mp'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)