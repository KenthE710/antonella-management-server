from django.db import models, transaction

from core.models import AuditModel


class Cliente(AuditModel):
    """
    Modelo que representa a un cliente.
    Atributos:
    - nombre (str): El nombre del cliente.
    - apellido (str): El apellido del cliente.
    - email (str): El correo electrónico del cliente.
    - telefono (str): El número de teléfono del cliente.
    - direccion (str): La dirección del cliente.
    - fecha_nacimiento (date): La fecha de nacimiento del cliente.
    - cedula (str): La cédula del cliente.
    
    Métodos:
    - __str__(): La representación en cadena del cliente.
    """

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    #notas = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.servicios_realizados.all().delete()
        
        super().delete(using, keep_parents)