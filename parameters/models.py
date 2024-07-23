from django.db import models

from core.models import AuditModel


class Parametro(AuditModel):
    """
    Modelo de datos para un parámetro del sistema.

    El modelo `Parametro` representa un parámetro del sistema con un código único, una descripción opcional y un valor. Este modelo se utiliza para almacenar y gestionar los parámetros de configuración del sistema.

    Atributos:
        codigo (CharField): Código único del parámetro (máximo 25 caracteres).
        descripcion (CharField): Descripción opcional del parámetro (máximo 225 caracteres).
        valor (CharField): Valor del parámetro (máximo 100 caracteres).

    Métodos:
        __str__(): Devuelve el código del parámetro como representación en cadena.
    """

    codigo = models.CharField(max_length=25, unique=True)
    valor = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.codigo
