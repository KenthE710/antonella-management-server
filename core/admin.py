from django.contrib import admin

from .models import ServicioEspecialidad

admin.site.site_header = "Administración de Antonella Management"
admin.site.site_title = "Antonella Management"
admin.site.index_title = "Bienvenido a Antonella Management"

admin.site.register(ServicioEspecialidad)
