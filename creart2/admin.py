from django.contrib import admin
from .models import Roles, Usuarios, Solicitud, Producto, Permisos, PQRS, Transaccion

# Register your models here.
admin.site.register(Roles)
admin.site.register(Usuarios)   
admin.site.register(Solicitud)
admin.site.register(Producto)
admin.site.register(Permisos)
admin.site.register(PQRS)
admin.site.register(Transaccion)

