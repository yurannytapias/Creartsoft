"""
URL configuration for Creartsoft project.

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
from creart2 import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path ('inicio/', views.inicio, name='inicio'),
    path ('index/', views.index, name='inicio'),
    path ('cliente/', views.cliente, name='cliente'),
    path ('administrador/', views.administrador, name='administrador'),
    path ('vendedor/', views.vendedor, name='vendedor'),
    path('solicitud/', views.solicitudes, name='solicitudes'),
    path("mi_perfil/", views.mi_perfil, name="mi_perfil"),
    path('producto/', views.productos, name='productos'),
    path('producto_especifico/', views.productos, name='producto_especifico'),
    path('solicitud', views.solicitudes, name='solicitudes.html'),
    path('solicitudes_vendedor', views.solicitudes_vendedor, name='solicitudes'),
    path('editar_solicitud', views.editar_solicitud, name='editar_solicitud'),
    path('gestionar_producto', views.gestionar_producto, name='gestionar_producto'),
    path('editar_producto', views.editar_produjnghjfgjfghdcto, name='editar_producto'),
    path('', views.index, name='home'),
]
