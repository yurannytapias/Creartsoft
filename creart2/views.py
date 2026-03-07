from django.shortcuts import render
from .models import Usuarios, Solicitud, Transaccion, Producto


def index(request):
    return render(request, 'index.html')


def inicio(request):
    return render(request, 'inicio.html')

def cliente(request):
    return render(request, 'cliente.html')

def administrador(request):
    return render(request, 'administrador.html')

def vendedor(request):
    return render(request, 'vendedor.html')

def mi_perfil(request):
    return render(request, 'mi_perfil.html')


def pqrs(request):
    return render (request, 'pqrs.html')

def crear_pqrs(request):
    return render(request, 'crear_pqrs.html')

def solicitudes(request):
    solicitud = Solicitud.object.all()
    
    contexto = {
        'solicitudes.html': solicitud
    }

    return render(request, 'solicitudes.html')

def crear_solicitud(request):
    return render(request, 'crear_solicitud.html')

def solicitudes_vendedor(request):
    return render(request, 'solicitudes_vendedor')

def productos(request):
    productos = Producto.object.all()
    
    contexto = {
        'productos.html': productos
    }
    
    return render(request, 'productos.html')

def crear_producto(request):
    return render(request, 'crear_producto.html')

def gestionar_producto(request):
    return render (request, 'gestionar_producto')

def editar_producto(request):
    return render (request, 'editar_producto.html')

def aceptar_solicitud(request):
    return render (request, 'aceptar_solicitud.html')

def editar_solicitud(request):
    return render (request, "editar_solicitud.html")    

def transacciones(request):
    transaccion = Transaccion.object.all()
    
    contexto = {
        'transacciones.html': transaccion
    }
    
    return render(request, 'transacciones.html')


