from django.db import models

from core.models import AuditModel


class Cliente(AuditModel):
    """
    Modelo de base de datos que representa a un cliente en el sistema de gestión de Antonella.

    Atributos:
        nombre (str): El nombre del cliente.
        apellido (str): El apellido del cliente.

    Métodos:
        __str__(): Devuelve una representación en cadena del cliente en el formato "nombre apellido".
    """

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
