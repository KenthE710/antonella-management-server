from django.db import models, transaction

from core.models import AuditModel, ServicioEspecialidad

class PersonalState(AuditModel):
    """
    Modelo que representa el estado personal.
    Atributos:
    - name (str): Nombre del estado personal.
    Métodos:
    - save(*args, **kwargs): Sobrescribe el método save para convertir el nombre a mayúsculas antes de guardar el objeto.
    - __str__(): Retorna una representación en cadena del estado personal.
    """

    
    name = models.CharField(max_length=50, unique=True)
    
    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.personal.update(estado=None)
        
        super().delete(using, keep_parents)

class Personal(AuditModel):
    """
    Modelo que representa al personal del sistema.
    Atributos:
    - nombre (str): El nombre del personal.
    - apellido (str): El apellido del personal.
    - cedula (str): La cédula del personal (opcional).
    - email (str): El correo electrónico del personal (opcional).
    - telefono (str): El número de teléfono del personal (opcional).
    - direccion (str): La dirección del personal (opcional).
    - fecha_nacimiento (date): La fecha de nacimiento del personal (opcional).
    - estado (PersonalState): El estado del personal.
    Métodos:
    - __str__(): Devuelve una representación en cadena del personal.
    """
    
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    estado = models.ForeignKey(PersonalState, on_delete=models.SET_NULL, null=True, related_name='personal')
    especialidades = models.ManyToManyField(ServicioEspecialidad, related_name="personal", null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        self.servicios.update(encargado=None)
        
        super().delete(using, keep_parents)