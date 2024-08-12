from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db import models
from core.models import AuditModel
from os import path
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models.signals import post_delete
from django.db.models import Sum


class ProductoTipo(AuditModel):
    """
    Modelo de base de datos para el tipo de producto.

    Atributos:
    - nombre (str): Nombre del tipo de producto.
    - descripcion (str): Descripción del tipo de producto.

    Métodos:
    - __str__(): Devuelve el nombre del tipo de producto como representación en cadena.
    """

    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.nombre


class ProductoMarca(AuditModel):
    """
    Modelo de base de datos para la marca de un producto.

    Atributos:
    - nombre (str): Nombre de la marca del producto.

    Métodos:
    - __str__(): Devuelve el nombre de la marca del producto como representación en cadena.
    """

    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Producto(AuditModel):
    """
    Modelo de base de datos para un producto.

    Atributos:
    - tipo (ProductoTipo): Tipo de producto al que pertenece.
    - marca (ProductoMarca): Marca del producto, puede ser nula.
    - nombre (str): Nombre del producto.
    - sku (str): Código de identificación del producto, puede estar en blanco.
    - precio (Decimal): Precio del producto.
    - usos_est (int): Número estimado de usos del producto.

    Métodos:
    - __str__(): Devuelve el nombre del producto como representación en cadena.
    """

    tipo = models.ForeignKey(ProductoTipo, on_delete=models.CASCADE)
    marca = models.ForeignKey(
        ProductoMarca, on_delete=models.SET_NULL, null=True, blank=True
    )
    nombre = models.CharField(max_length=50)
    sku = models.CharField(max_length=25, blank=True, null=True)
    precio = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    usos_est = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre
    
    @property
    def posee_existencias(self):
        lotes = self.lotes.filter(retirado=False, fe_exp__gt=timezone.now())
        for lote in lotes:
            if lote.servicios_restantes > 0:
                return True
    
        return False
    
    @property
    def existencias(self):
        lotes = self.lotes.filter(retirado=False, fe_exp__gt=timezone.now())
        return sum([lote.cant if not lote.consumido else 0 for lote in lotes])
    
    @property
    def usos_restantes(self):
        lotes = self.lotes.filter(retirado=False, fe_exp__gt=timezone.now())
        return sum([lote.servicios_restantes for lote in lotes])
    
    @property
    def getLoteToUse(self):
        lotes = self.lotes.filter(retirado=False, fe_exp__gt=timezone.now()).order_by('fe_exp').all()
        
        for lote in lotes:
            if lote.servicios_restantes > 0:
                return lote


class ProductoImg(AuditModel):
    """
    Modelo de base de datos para una imagen de un producto.

    Atributos:
    - producto (Producto): Producto al que pertenece la imagen.
    - imagen (str): Archivo de imagen del producto.
    - url_imagen_externa (str): URL de la imagen del producto.
    - nombre (str): Nombre del producto.
    - is_cover (bool): Indica si la imagen es la portada del producto.
    - is_temp (bool): Indica si la imagen es temporal.

    Métodos:
    - __str__(): Devuelve la URL de la imagen como representación en cadena.
    """

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="imgs", blank=True, null=True
    )
    imagen = models.ImageField(upload_to="img/", blank=True, null=True)
    url_imagen_externa = models.URLField(max_length=2083, blank=True, null=True)
    is_cover = models.BooleanField(default=False)
    is_temp = models.BooleanField(default=False)

    def __str__(self):
        if self.imagen:
            return self.imagen.url
        elif self.url_imagen_externa:
            return self.url_imagen_externa
        else:
            return ""

    @property
    def name(self):
        if self.imagen and self.imagen.name:
            return path.basename(self.imagen.name)
        else:
            return ""

    @property
    def url(self):
        if self.imagen and self.imagen.name:
            # return self.imagen.storage.url(self.imagen.name)
            """ if self.imagen.url.startswith("http"):
                return self.imagen.url
            return f"{settings.DOMINIO}{self.imagen.url}" """
            return self.imagen.url
        elif self.url_imagen_externa:
            return self.url_imagen_externa
        else:
            return ""


class Lote(AuditModel):
    """
    Modelo de base de datos para un lote de productos.

    Atributos:
    - producto (Producto): Producto al que pertenece el lote.
    - fe_compra (datetime): Fecha y hora de compra del lote, puede estar en blanco.
    - fe_exp (datetime): Fecha y hora de expiración del lote, puede estar en blanco.
    - cant (int): Cantidad de productos en el lote.
    - costo (Decimal): Costo del lote.
    - consumido (bool): Indica si el lote ha sido consumido.
    - retirado (bool): Indica si el lote ha sido retirado.

    Métodos:
    - __str__(): Devuelve una representación en cadena del lote con el nombre del producto.
    """

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="lotes")
    fe_compra = models.DateTimeField(blank=True, null=True)
    fe_exp = models.DateTimeField(blank=True, null=True)
    cant = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    costo = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    retirado = models.BooleanField(default=False)

    def __str__(self):
        return f"Lote de {self.producto.nombre}"

    def clean(self):
        if self.costo >= self.producto.precio:
            raise ValidationError(
                "El costo del lote debe ser menor que el precio del producto asociado."
            )
            
    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)
        post_delete.send(sender=self.__class__, instance=self)
    
    def is_expired(self):
        if self.fe_exp:
            return self.fe_exp < timezone.now()
        return False
    
    @property
    def consumido(self):
        return self.servicios_restantes == 0

    @property
    def state(self):
        if self.consumido:
            return 1 #"Consumido"
        elif self.retirado:
            return 2 #"Retirado"
        elif self.is_expired():
            return 3 #"Vencido"
        return 0 #"Activo"

    @property
    def servicios_Realizados(self):
        from services.models import ServicioRealizadoProducto
        return ServicioRealizadoProducto.objects.active().filter(lote=self).aggregate(Sum('cantidad', default=0))["cantidad__sum"] or 0
    
    @property
    def servicios_restantes(self):
        return self.producto.usos_est * self.cant - self.servicios_Realizados
