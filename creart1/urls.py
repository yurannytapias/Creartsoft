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
    path('', views.mi_vista, name='index'),
    path('usuarios/', views.mi_lista_usuarios, name='usuarios'),
    path('inicio/', views.inicio, name='inicio'),
    path('vendedor/', views.vendedor, name='vendedor'),
    path('vendedor_solicitudes/', views.solicitudes_vendedor, name='vendedor_solicitudes'),
    path('vendedor_ventas/', views.ventas_vendedor, name='vendedor_ventas'),
    path('vendedor_clientes/', views.clientes_vendedor, name='vendedor_clientes'),
    path('vendedor_productos/', views.productos_vendedor, name='vendedor_productos'),
    path('vendedor_bonos/', views.bonos_vendedor, name='vendedor_bonos'),
    path('vendedor_perfil/', views.mi_perfil_vendedor, name='vendedor_perfil'),
    path('vendedor_reportes/', views.reportes_vendedor, name='vendedor_reportes'),
    path('login/', views.login_usuario, name='login'),
    path('registro/', views.registrar_usuario, name='registro'),
    path('cerrar_sesion/', views.logout_usuario, name='cerrar_sesion')
]
