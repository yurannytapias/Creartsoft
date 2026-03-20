from django.db import models

class ModeloBase(models.Model):
    # auto_now_add: se pone solo al crear
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # auto_now: se actualiza solo cada vez que guardas (save)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.BooleanField(default=True)

    class Meta:
        abstract = True #agregar siempre que la clase sea abstracta
        
class Roles(ModeloBase):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=225)
    descripcion = models.CharField(max_length=225)

class Permisos(ModeloBase):
    id_permiso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=225)
    descripcion = models.CharField(max_length=225)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)
    
class Usuarios(ModeloBase):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=225)
    documento = models.CharField(max_length=225)
    apellido = models.CharField(max_length=225)
    correo = models.CharField(max_length=225)
    numero = models.CharField(max_length=225)
    contrasena = models.CharField(max_length=255)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)

class Productos(ModeloBase):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=225)
    descripcion = models.CharField(max_length=225)
    precio = models.CharField(max_length=225)
    imagen = models.CharField(max_length=225)
    vendedor = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    
class Solicitudes(ModeloBase):
    id_solicitud = models.AutoField(primary_key=True)
    detalles = models.CharField(max_length=225)
    cantidad = models.CharField(max_length=225)
    cliente = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)

class Transaccion(ModeloBase):
    id_pedido = models.AutoField(primary_key=True)
    id_transaccion = models.IntegerField(unique=True) 
    hora = models.TimeField()
    importe_total  = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=225)
    comisiones  = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=225)
    token = models.CharField(max_length=225)
    ip_cliente = models.CharField(max_length=225)
    solicitud = models.ForeignKey(Solicitudes, on_delete=models.CASCADE)
    
class PQRS(ModeloBase):
    id_pqrs = models.AutoField(primary_key=True)
    causa_problema = models.CharField(max_length=225)
    mensaje = models.CharField(max_length=225)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)

