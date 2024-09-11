from decimal import Decimal
from os import path
from typing import Iterable
from django.db import models, transaction
from django.utils import timezone

from core.models import AuditModel
from inventory.models import Lote, Producto
from staff.models import Personal
from customers.models import Cliente
from .managers import ServicioManager


class ServicioEstado(AuditModel):
    """
    Modelo que representa un estado de servicio.
    Atributos:
    - nombre: El nombre del estado del servicio.
    - descripcion: La descripción del estado del servicio.
    Métodos:
    - save: Guarda el estado del servicio en la base de datos.
    - __str__: Devuelve una representación en cadena del estado del servicio.
    """
    
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=225, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.servicios.update(estado=None)
        
        super().delete(using, keep_parents)


class Servicio(AuditModel):
    """
    Clase que representa un servicio.
    Atributos:
    - nombre: El nombre del servicio (max_length=100).
    - descripcion: La descripción del servicio (max_length=225, opcional).
    - precio: El precio del servicio (Decimal de 6 dígitos y 2 decimales, por defecto 0.00).
    - tiempo_est: El tiempo estimado del servicio (opcional).
    - encargado: El encargado del servicio (ForeignKey a Personal, cuando se elimina se establece como NULL, opcional).
    - productos: Los productos asociados al servicio (ManyToManyField a Producto, relacionados como "servicios", opcional).
    - estado: El estado del servicio (ForeignKey a ServicioEstado, cuando se elimina se establece como NULL, opcional).
    Métodos:
    - __str__: Retorna el nombre del servicio.
    - save: Guarda el servicio en la base de datos. Si el estado es None, se establece como "ACTIVO".
    - get_disponibilidad: Retorna True si todos los productos asociados al servicio tienen existencias, False de lo contrario.
    """
    
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=225, blank=True, null=True)
    precio = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    tiempo_est = models.DurationField(blank=True, null=True)
    encargado = models.ForeignKey(
        Personal, on_delete=models.SET_NULL, null=True, related_name="servicios"
    )
    productos = models.ManyToManyField(Producto, related_name="servicios", null=True)
    estado = models.ForeignKey(ServicioEstado, on_delete=models.SET_NULL, null=True, related_name="servicios")

    objects = ServicioManager()

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if self.estado is None:
            self.estado = ServicioEstado.objects.get_or_create(nombre="ACTIVO")[0]

        super().save(*args, **kwargs)

    @property
    def get_disponibilidad(self):
        if all(
            producto.get_posee_existencias for producto in self.productos.active().all()
        ):
            return True
        return False

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.imagenes.all().delete()
        self.servicios_realizados.all().delete()
        
        super().delete(using, keep_parents)

class ServicioImg(AuditModel):
    """
    Modelo para representar una imagen de servicio.
    Atributos:
    - servicio: ForeignKey al modelo Servicio, indica el servicio al que pertenece la imagen.
    - imagen: ImagenField, almacena la imagen del servicio.
    - is_cover: BooleanField, indica si la imagen es la imagen de portada del servicio.
    - is_tmp: BooleanField, indica si la imagen es temporal.
    Métodos:
    - __str__(): Devuelve una representación legible en cadena del objeto.
    - name: Propiedad que devuelve el nombre de la imagen.
    """
    
    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE, null=True, related_name="imagenes"
    )
    imagen = models.ImageField(upload_to="img/servicios/", null=True)
    is_cover = models.BooleanField(default=False)
    is_tmp = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.servicio} - {self.name}"

    @property
    def name(self):
        if self.imagen and self.imagen.name:
            return path.basename(self.imagen.name)
        else:
            return ""


class ServicioRealizado(AuditModel):
    """
    Modelo que representa un servicio realizado por un cliente.
    Atributos:
    - cliente: ForeignKey a la instancia del cliente que realizó el servicio.
    - servicio: ForeignKey a la instancia del servicio realizado.
    - fecha: Fecha y hora en que se realizó el servicio. Por defecto, es la fecha y hora actual.
    - pagado: Monto pagado por el servicio realizado. Por defecto, es 0.00.
    - finalizado: Indica si el servicio ha sido finalizado o no. Por defecto, es False.
    Métodos:
    - __str__: Devuelve una representación en cadena del servicio realizado, en el formato "cliente - servicio".
    """
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="servicios_realizados")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="servicios_realizados")
    fecha = models.DateTimeField(default=timezone.now())
    pagado = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente} - {self.servicio}"

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.productos_utilizados.all().delete()
        
        super().delete(using, keep_parents)

class ServicioRealizadoProducto(AuditModel):
    """
    Modelo que representa un producto utilizado en un servicio realizado.
    Atributos:
    - servicio_realizado: El servicio realizado al que pertenece este producto utilizado.
    - producto: El producto utilizado.
    - lote: El lote del producto utilizado.
    - cantidad: La cantidad utilizada del producto (usos).
    Métodos:
    - __str__: Devuelve una representación en cadena del objeto.
    """
    
    servicio_realizado = models.ForeignKey(
        ServicioRealizado, on_delete=models.CASCADE, related_name="productos_utilizados"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="servicio_realizado_productos")
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="servicio_realizado_productos")
    cantidad = models.PositiveIntegerField() # Cantidad utilizada del producto (usos)

    def __str__(self):
        return f"{self.servicio_realizado} - {self.producto} - {self.cantidad}"
