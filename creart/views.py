from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Roles, Permisos, Usuarios, Solicitudes, Productos, PQRS, Transaccion
from django.contrib.auth.hashers import make_password, check_password

def mi_vista(request):
    return render(request, 'index.html')
# Create your views here.

def mi_lista_usuarios(request):
    usuarios_bd = Usuarios.objects.all()
    
    contexto = {
        'lista_usuarios': usuarios_bd
    }
    
    return render(request, 'lista_usuarios.html', contexto)

def vendedor(request):

    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'vendedor.html', contexto)

def solicitudes_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'solicitudes_vendedor.html')

def ventas_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'ventas_vendedor.html')

def clientes_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'vendedor_clientes.html')

def productos_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'productos_vendedor.html')

def reportes_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'reportes_vendedor.html')

def bonos_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'bonos_vendedor.html')

def mi_perfil_vendedor(request):
    if 'usuario_id' not in request.session:
        return redirect('inicio')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])

    contexto = {
        'usuario': usuario
    }

    return render(request, 'perfil_vendedor.html')

def inicio(request):

    return render(request, 'inicio.html')

def registrar_usuario(request):
    if request.method == "POST":
        documento = request.POST['documento']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        correo = request.POST['correo']
        numero = request.POST['numero']
        contrasena = make_password(request.POST['contrasena'])

        rol_vendedor = Roles.objects.get(nombre="vendedor")

        nuevo_usuario = Usuarios.objects.create(
            documento=documento,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            numero=numero,
            contrasena=contrasena,
            rol=rol_vendedor
        )

        return redirect('inicio')

    return render(request, 'inicio.html')

def login_usuario(request):

    if request.method == "POST":

        correo = request.POST['correo']
        contrasena = request.POST['contrasena']

        try:
            usuario = Usuarios.objects.get(correo=correo)

            if check_password(contrasena, usuario.contrasena):

                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre

                return redirect('vendedor')

            else:
                return render(request, 'inicio.html', {'error': 'Contraseña incorrecta'})

        except Usuarios.DoesNotExist:
            return render(request, 'inicio.html', {'error': 'Usuario no existe'})

def logout_usuario(request):
    request.session.flush()
    return redirect('inicio')