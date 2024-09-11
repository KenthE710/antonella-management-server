from django.db import models
from django.utils import timezone


class AuditQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def inactive(self):
        return self.filter(deleted_at__isnull=False)


class AuditManager(models.Manager):
    def get_queryset(self):
        return AuditQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()


class AuditModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría para el seguimiento de la creación, actualización y eliminación de registros.
    Atributos:
        created_by (str): El usuario que creó el registro.
        created_at (datetime): La fecha y hora de creación del registro.
        updated_by (str): El usuario que actualizó por última vez el registro.
        updated_at (datetime): La fecha y hora de la última actualización del registro.
        deleted_by (str): El usuario que eliminó el registro.
        deleted_at (datetime): La fecha y hora de eliminación del registro.
    Métodos:
        delete(using=None, keep_parents=False): Marca el registro como eliminado estableciendo la fecha y hora de eliminación.
        hard_delete(): Elimina permanentemente el registro de la base de datos.
        is_deleted(): Verifica si el registro ha sido eliminado.
    Meta:
    """
    
    created_by = models.CharField(max_length=25, default="root", editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.CharField(max_length=25, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_by = models.CharField(max_length=25, null=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
        ordering = ["created_at"]
        get_latest_by = "created_at"

    objects = AuditManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    def is_deleted(self):
        return self.deleted_at is not None

