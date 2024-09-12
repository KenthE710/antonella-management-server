from os import path
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from core.models import AuditModel
from inventory.managers import LoteManager, ProductoManager


class ProductoTipo(AuditModel):
    """
    Modelo que representa un tipo de producto en el inventario.
    Atributos:
    - nombre: El nombre del tipo de producto (max_length=50, unique=True).
    - descripcion: La descripción del tipo de producto (max_length=225, blank=True, null=True).
    Métodos:
    - __str__: Devuelve el nombre del tipo de producto.
    """
    
    
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.nombre

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.productos.all().delete()
        return super().delete(using, keep_parents)

class ProductoMarca(AuditModel):
    """
    Modelo que representa una marca de producto.
    Atributos:
    - nombre: El nombre de la marca (cadena de caracteres).
    Métodos:
    - __str__: Devuelve una representación en cadena de la marca.
    """

    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.productos.all().delete()
        return super().delete(using, keep_parents)

class Producto(AuditModel):
    """
    Modelo que representa un producto en el inventario.
    Atributos:
    - tipo: El tipo de producto al que pertenece (ForeignKey a ProductoTipo).
    - marca: La marca del producto (ForeignKey a ProductoMarca).
    - nombre: El nombre del producto (CharField de longitud máxima 50).
    - sku: El código SKU del producto (CharField de longitud máxima 25, opcional).
    - precio: El precio del producto (DecimalField con 6 dígitos y 2 decimales, valor predeterminado: 0.00).
    - usos_est: El número de usos estimados del producto (IntegerField, valor predeterminado: 0).
    Métodos:
    - __str__: Devuelve una representación en cadena del producto.
    - get_posee_existencias: Devuelve True si el producto tiene existencias disponibles, False en caso contrario.
    - get_existencias: Devuelve la cantidad total de existencias del producto.
    - get_usos_restantes: Devuelve el número total de usos restantes del producto.
    - get_lote_to_use: Devuelve el lote más próximo a expirar que tiene usos restantes.
    """

    tipo = models.ForeignKey(ProductoTipo, on_delete=models.SET_NULL, null=True, related_name="productos")
    marca = models.ForeignKey(
        ProductoMarca, on_delete=models.SET_NULL, null=True, related_name="productos"
    )
    nombre = models.CharField(max_length=50)
    sku = models.CharField(max_length=25, null=True)
    precio = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    usos_est = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre
    
    objects = ProductoManager()
    
    @property
    def get_posee_existencias(self):
        lotes = self.lotes.active().filter(retirado=False, fe_exp__gt=timezone.now())
        for lote in lotes:
            if lote.get_servicios_restantes > 0:
                return True
    
        return False
    
    @property
    def get_existencias(self):
        lotes = self.lotes.active().filter(retirado=False, fe_exp__gt=timezone.now())
        return sum([lote.cant if not lote.get_consumido else 0 for lote in lotes])
    
    @property
    def get_usos_restantes(self):
        lotes = self.lotes.active().filter(retirado=False, fe_exp__gt=timezone.now())
        return sum([lote.get_servicios_restantes for lote in lotes])
    
    @property
    def get_lote_to_use(self):
        lotes = self.lotes.active().filter(retirado=False, fe_exp__gt=timezone.now()).order_by('fe_exp').all()
        
        for lote in lotes:
            if lote.get_servicios_restantes > 0:
                return lote

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.imgs.all().delete()
        self.lotes.all().delete()
        self.servicios.clear()
        self.servicio_realizado_productos.all().delete()
        
        return super().delete(using, keep_parents)

class ProductoImg(AuditModel):
    """
    Modelo que representa una imagen de un producto.
    Atributos:
    - producto: El producto al que pertenece la imagen.
    - imagen: La imagen del producto.
    - url_imagen_externa: La URL de una imagen externa.
    - is_cover: Indica si la imagen es la imagen de portada del producto.
    - is_temp: Indica si la imagen es temporal.
    Métodos:
    - __str__: Devuelve la URL de la imagen o la URL de la imagen externa.
    - name: Devuelve el nombre de la imagen.
    - url: Devuelve la URL de la imagen o la URL de la imagen externa.
    """    

    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, related_name="imgs"
    )
    imagen = models.ImageField(upload_to="img/productos/", null=True)
    url_imagen_externa = models.URLField(max_length=2083, null=True)
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
    Clase que representa un lote de productos.
    Atributos:
    - producto: Producto al que pertenece el lote.
    - fe_compra: Fecha y hora de compra del lote (opcional).
    - fe_exp: Fecha y hora de expiración del lote (opcional).
    - cant: Cantidad de productos en el lote (por defecto: 1).
    - costo: Costo del lote (por defecto: 0.00).
    - motivo: Motivo de la eliminación del lote (opcional).
    - retirado: Indica si el lote ha sido retirado (por defecto: False).
    Métodos:
    - __str__(): Devuelve una representación en cadena del lote.
    - clean(): Valida que el costo del lote sea menor al precio del producto asociado.
    - delete(using=None, keep_parents=False): Elimina el lote y envía una señal de eliminación.
    - is_expired(): Verifica si el lote ha expirado.
    - get_consumido: Propiedad que indica si el lote ha sido completamente consumido.
    - get_state: Propiedad que devuelve el estado del lote (0: Activo, 1: Consumido, 2: Retirado, 3: Vencido).
    - get_servicios_Realizados: Propiedad que devuelve la cantidad de servicios realizados con el lote.
    - get_servicios_restantes: Propiedad que devuelve la cantidad de servicios restantes para el lote.
    """    

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="lotes")
    fe_compra = models.DateTimeField(blank=True, null=True)
    fe_exp = models.DateTimeField(blank=True, null=True)
    cant = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    costo = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    motivo = models.CharField(max_length=225, blank=True, null=True)
    #TODO: Definir como un campo de estado
    retirado = models.BooleanField(default=False)

    def __str__(self):
        return f"Lote de {self.producto.nombre}"

    objects = LoteManager()

    def clean(self):
        if self.costo >= self.producto.precio:
            raise ValidationError(
                "El costo del lote debe ser menor que el precio del producto asociado."
            )
            
    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.servicio_realizado_productos.all().delete()
        
        super().delete(using, keep_parents)
        post_delete.send(sender=self.__class__, instance=self)
    
    def is_expired(self):
        if self.fe_exp:
            return self.fe_exp < timezone.now()
        return False
    
    @property
    def get_consumido(self):
        return self.get_servicios_restantes == 0

    @property
    def get_state(self):
        if self.get_consumido:
            return 1 #"Consumido"
        elif self.retirado:
            return 2 #"Retirado"
        elif self.is_expired():
            return 3 #"Vencido"
        return 0 #"Activo"

    @property
    def get_servicios_Realizados(self):
        from services.models import ServicioRealizadoProducto
        return ServicioRealizadoProducto.objects.active().filter(lote=self).aggregate(Sum('cantidad', default=0))["cantidad__sum"] or 0
    
    @property
    def get_servicios_restantes(self):
        return self.producto.usos_est * self.cant - self.get_servicios_Realizados
