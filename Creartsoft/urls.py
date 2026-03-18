from django.contrib import admin
from django.urls import path
from creart2 import views

urlpatterns = [
    path('admin/',          admin.site.urls),

    # ── Públicas ──
    path('',                views.index,                name='home'),
    path('index/',          views.index,                name='index'),
    path('inicio/',         views.inicio,               name='inicio'),

    # ── Autenticación ──
    path('login/',          views.login,                name='login'),
    path('register/',       views.register,             name='register'),
    path('cerrar-sesion/',  views.cerrar_sesion,        name='cerrar_sesion'),

    # ── Admin ──
    path('administrador/',  views.administrador,        name='administrador'),
    path('transacciones/',  views.transacciones,        name='transacciones'),
    path('usuarios/',       views.usuarios,             name='usuarios'),
    path('pqrs/',           views.pqrs,                 name='pqrs'),
    path('pqrs/<int:pk>/responder/', views.pqrs_responder, name='pqrs_responder'),
    path('perfil/',         views.administrador_perfil, name='administrador_perfil'),
]