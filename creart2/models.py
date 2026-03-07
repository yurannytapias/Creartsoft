from django.db import models

# Create your models here.
#tabla 1: Roles
class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre
    
    
#tabla 2: Usuarios
class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    numero = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    contrasena = models.CharField(max_length=128)
    
    Roles = models.ForeignKey(Roles, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    
#tabla 3: Solicitud
class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    detalles = models.TextField()
    cantidad = models.IntegerField()
    
    Usuarios = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Solicitud {self.id_solicitud} - Usuario: {self.Usuarios.nombre}"        
 
    
#tabla 4: Producto
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    
    Solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre 
    
#tabla 5: Permisos 
class Permisos(models.Model):
    id_permiso = models.AutoField(primary_key=True)
    descripcion = models.TextField()
    
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.descripcion
    
#tabla 6: PQRS
class PQRS(models.Model):
    id_pqrs = models.AutoField(primary_key=True)
    causa_problema = models.TextField()
    mensaje = models.TextField()
    
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Reporte {self.id_pqrs} - Usuario: {self.Usuarios.nombre}"
    
#tabla 7: Transaccion 
class Transaccion(models.Model):
    id_transaccion = models.AutoField(primary_key=True)
    id_pedido = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10)
    comision = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    token_tarjeta = models.CharField(max_length=100)
    IP_cliente = models.GenericIPAddressField()
    
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Transacción {self.id_transaccion} - Pedido: {self.id_pedido}"
        
    
