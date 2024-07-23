from decimal import Decimal
from django.db import models
from core.models import AuditModel


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

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.nombre


class ProductoImg(AuditModel):
    """
    Modelo de base de datos para una imagen de un producto.

    Atributos:
    - producto (Producto): Producto al que pertenece la imagen.
    - imagen (str): Archivo de imagen del producto.
    - url_imagen_externa (str): URL de la imagen del producto.
    - is_cover (bool): Indica si la imagen es la portada del producto.
    - is_temp (bool): Indica si la imagen es temporal.

    Métodos:
    - __str__(): Devuelve la URL de la imagen como representación en cadena.
    """

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="imgs"
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


class Lote(AuditModel):
    """
    Modelo de base de datos para un lote de productos.

    Atributos:
    - producto (Producto): Producto al que pertenece el lote.
    - fe_compra (datetime): Fecha y hora de compra del lote, puede estar en blanco.
    - fe_exp (datetime): Fecha y hora de expiración del lote, puede estar en blanco.
    - cant (int): Cantidad de productos en el lote.
    - costo (Decimal): Costo del lote.

    Métodos:
    - __str__(): Devuelve una representación en cadena del lote con el nombre del producto.
    """

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fe_compra = models.DateTimeField(blank=True, null=True)
    fe_exp = models.DateTimeField(blank=True, null=True)
    cant = models.PositiveIntegerField(default=0)
    costo = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"Lote de {self.producto.nombre}"
