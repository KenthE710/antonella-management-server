from django.db import models

from core.models import AuditModel


class Parametro(AuditModel):
    """
    Clase que representa un parámetro.
    Atributos:
    - codigo: Código del parámetro (max_length=25, unique=True).
    - valor: Valor del parámetro (max_length=100, blank=True, null=True).
    - descripcion: Descripción del parámetro (max_length=225, blank=True, null=True).
    Métodos:
    - __str__: Devuelve el código del parámetro.
    """
    
    codigo = models.CharField(max_length=25, unique=True)
    valor = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.codigo
