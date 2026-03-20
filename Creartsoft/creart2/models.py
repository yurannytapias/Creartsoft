from django.db import models

# Create your models here.
class Roles (models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)   

    def __str__(self):
        return self.nombre

class Usuarios (models.Model):

    id_usuario = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=20)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField(max_length=100)
    numero_telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    contraseña = models.CharField(max_length=100)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Productos (models.Model):
    CATEGORIAS = [
        ('antojos', 'Antojos'),
        ('eventos', 'Eventos'),
        ('diarios', 'Diarios'),
    ]
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='diarios')

    def __str__(self):
        return self.nombre
    
class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('pagada', 'Pagada'),
    ]

    id_solicitud = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)

    # Datos comprador sin registro
    nombre_invitado = models.CharField(max_length=100, blank=True)
    direccion_entrega = models.CharField(max_length=200, blank=True)
    tipo_entrega = models.CharField(max_length=20, default='tienda')

    # Personalización
    descripcion = models.TextField(blank=True)
    mensaje_pastel = models.CharField(max_length=28, blank=True)
    cobertura = models.CharField(max_length=50, blank=True)
    rellenos = models.CharField(max_length=200, blank=True)
    decoracion = models.CharField(max_length=200, blank=True)
    pisos = models.IntegerField(default=1)
    porciones = models.IntegerField(null=True, blank=True)
    fecha_evento = models.DateField(null=True, blank=True)

    # Precio y estado
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    abono = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    # MercadoPago
    mp_preference_id = models.CharField(max_length=200, blank=True)
    mp_payment_id = models.CharField(max_length=200, blank=True)
class Permisos(models.Model):
    id_permiso = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    
    def __str__(self):
        return self.descripcion  # ← cambia self.nombre por self.descripcion
class Pqrs (models.Model):
    id_pqrs = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} de {self.usuario.nombre}"
    
class Transaccion(models.Model):
    ESTADOS = [
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('pendiente', 'Pendiente'),
    ]

    id_transaccion = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10, default='COP')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    metodo_pago = models.CharField(max_length=50, blank=True)
    mp_payment_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Transacción #{self.id_transaccion} — {self.estado}" #Esto es para mostrar el id y el estado de la transacción en el admin de django
