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
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

class Permisos(ModeloBase):
    id_permiso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)
    
class Usuarios(ModeloBase):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    contrasena = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)

class Productos(ModeloBase):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado')
    ]
    
    CATEGORIA = [
        ('antojos', 'Antojos'),
        ('eventos', 'Eventos'),
        ('diarios', 'Diarios'), 
    ]
    
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    motivo_rechazo = models.TextField(blank=True, null=True)
    vendedor = models.ForeignKey(Usuarios, on_delete=models.CASCADE)

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA,
        default='diarios'
    )

    estado_aprobacion = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    
class Solicitudes(ModeloBase):
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


class Transacciones(ModeloBase):
    ESTADOS_ABONO = [
        ('abonado', 'Abonado'),
        ('terminado', 'Terminado')
    ]


    id_transaccion = models.AutoField(primary_key=True)
    hora = models.TimeField()
    importe_total  = models.DecimalField(max_digits=10, decimal_places=2) #e el pago total
    moneda = models.CharField(max_length=225)
    comisiones  = models.DecimalField(max_digits=10, decimal_places=2) #son pagos adicionales como iva,lo que se lleva el banco, etc
    metodo_pago = models.CharField(max_length=225, blank=True)
    token = models.CharField(max_length=225)  #tarjeta de credito cifrada e incompleta
    ip_cliente = models.CharField(max_length=225) #seguridad o actividad fraudulenta
    solicitud = models.ForeignKey(Solicitudes, on_delete=models.CASCADE, blank=True)
    mp_payment_id = models.CharField(max_length=200, blank=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_ABONO,
        default='abonado'
    )
    
class PQRS(ModeloBase):
    ESTADO_CHOICES = [
        ('sin_respuesta', 'Sin_respuesta'),
        ('respondido', 'Respondido'),
    ]

    CATEGORIA = [
        ('pregunta', 'Pregunta'),
        ('queja', 'Queja'),
        ('reporte', 'Reporte'),
        ('solicitud', 'Solicitud')
    ]

    id_pqrs = models.AutoField(primary_key=True)
    asunto = models.CharField(max_length=225)
    mensaje = models.TextField()
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)

    estado_respuesta = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='sin_respuesta'
    )

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA,
        default='pregunta'
    )