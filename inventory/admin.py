from django.contrib import admin
from .models import Producto, ProductoImg, ProductoMarca, ProductoTipo, Lote

admin.site.register(Producto)
admin.site.register(ProductoTipo)
admin.site.register(ProductoMarca)
admin.site.register(ProductoImg)
admin.site.register(Lote)
