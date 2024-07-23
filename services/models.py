from decimal import Decimal
from django.db import models
from core.models import AuditModel
from inventory.models import Producto
from staff.models import Personal

class Servicio(AuditModel):
    """
    Representa un servicio ofrecido por la empresa. Cada servicio tiene un nombre, una descripción opcional, un precio, un tiempo estimado de ejecución, un encargado del personal, una lista de productos relacionados, y campos de auditoría como si ha sido eliminado, quién lo creó y modificó, y las fechas de creación y modificación.

    Atributos:
        nombre (CharField): Nombre del servicio.
        descripcion (CharField): Descripción del servicio.
        precio (DecimalField): Precio del servicio.
        tiempo_est (TimeField): Tiempo estimado de ejecución del servicio.
        encargado (ForeignKey): Encargado del personal asignado al servicio.
        productos (ManyToManyField): Lista de productos relacionados con el servicio.

    Métodos:
        __str__(): Devuelve el nombre del servicio como representación en cadena.
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=225, blank=True, null=True)
    precio = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    tiempo_est = models.TimeField(blank=True, null=True)
    encargado = models.ForeignKey(Personal, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, related_name="servicios")

    def __str__(self):
        return self.nombre
    