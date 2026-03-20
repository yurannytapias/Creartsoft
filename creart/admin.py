from django.contrib import admin
from .models import Roles, Usuarios, Permisos, Solicitudes, Productos, Transaccion, PQRS

# Register your models here.
admin.site.register(Roles)
admin.site.register(Usuarios)
admin.site.register(Permisos)
admin.site.register(Productos)
admin.site.register(Solicitudes)
admin.site.register(Transaccion)
admin.site.register(PQRS)