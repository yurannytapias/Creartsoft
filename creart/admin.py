from django.contrib import admin
from .models import Roles, Usuarios, Permisos, Solicitudes, Productos, Transacciones, PQRS

# Register your models here.
admin.site.register(Roles)
admin.site.register(Usuarios)
admin.site.register(Permisos)
admin.site.register(Productos)
admin.site.register(Solicitudes)
admin.site.register(Transacciones)
admin.site.register(PQRS)