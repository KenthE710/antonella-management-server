from decimal import Decimal
from django.db import models
from django.utils import timezone
from core.models import AuditModel
from inventory.models import Lote, Producto
from staff.models import Personal
from customers.models import Cliente

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
    tiempo_est = models.DurationField(blank=True, null=True)
    encargado = models.ForeignKey(Personal, on_delete=models.CASCADE, blank=True, null=True)
    productos = models.ManyToManyField(Producto, related_name="servicios")

    def __str__(self):
        return self.nombre
    
    @property
    def status(self):
        if all(producto.posee_existencias for producto in self.productos.all()):
            return 0;
        return 1;
    
class ServicioRealizado(AuditModel):
    """
    Representa un servicio realizado por un cliente. Cada servicio realizado tiene un cliente, un servicio, una fecha de realización, un estado de pago, un estado de finalización, y campos de auditoría como si ha sido eliminado, quién lo creó y modificó, y las fechas de creación y modificación.

    Atributos:
        cliente (ForeignKey): Cliente que solicitó el servicio.
        servicio (ForeignKey): Servicio realizado.
        fecha (DateTimeField): Fecha y hora de realización del servicio.
        pagado (DecimalField): Monto pagado por el servicio.
        finalizado (BooleanField): Estado de finalización del servicio.

    Métodos:
        __str__(): Devuelve el nombre del servicio realizado como representación en cadena.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now())
    pagado = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente} - {self.servicio}"
    
class ServicioRealizadoProducto(AuditModel):
    """
    Representa un producto utilizado en un servicio realizado. Cada producto utilizado tiene un servicio realizado, un producto, una cantidad utilizada, y campos de auditoría como si ha sido eliminado, quién lo creó y modificó, y las fechas de creación y modificación.

    Atributos:
        servicio_realizado (ForeignKey): Servicio realizado en el que se utilizó el producto.
        producto (ForeignKey): Producto utilizado.
        lote (ForeignKey): Lote del producto utilizado.
        cantidad (PositiveIntegerField): Cantidad utilizada del producto.

    Métodos:
        __str__(): Devuelve el nombre del producto utilizado como representación en cadena.
    """
    servicio_realizado = models.ForeignKey(ServicioRealizado, on_delete=models.CASCADE, related_name="productos_utilizados")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.servicio_realizado} - {self.producto} - {self.cantidad}"