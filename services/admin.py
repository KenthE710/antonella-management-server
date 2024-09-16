from django.contrib import admin
from .models import (
    Servicio,
    ServicioRealizado,
    ServicioRealizadoProducto,
    ServicioEstado,
    ServicioImg,
)

admin.site.register(Servicio)
admin.site.register(ServicioEstado)
admin.site.register(ServicioImg)
admin.site.register(ServicioRealizado)
admin.site.register(ServicioRealizadoProducto)
