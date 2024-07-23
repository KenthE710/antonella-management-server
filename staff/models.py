from django.db import models

from core.models import AuditModel


class Personal(AuditModel):
    """
    Modelo de datos para el registro de personal en el sistema de gestión de Antonella.

    La clase `Personal` representa la información básica de un miembro del personal, incluyendo:
    - Nombre y apellido
    - Número de cédula
    - Indicador de si el registro ha sido eliminado
    - Información de creación y modificación del registro (usuario y fecha)

    Los atributos de esta clase se utilizan para almacenar y gestionar la información del personal en la base de datos.
    """

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    cedula = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
