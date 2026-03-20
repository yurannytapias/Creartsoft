from django.contrib import admin
from .models import Roles, Usuarios, Permisos, Solicitud, Productos, Transaccion, Pqrs

admin.site.register(Roles)
admin.site.register(Usuarios)
admin.site.register(Permisos)
admin.site.register(Solicitud)
admin.site.register(Transaccion)
admin.site.register(Pqrs)

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio']