from core.models import AuditManager
from .querysets import ServicioQuerySet


class ServicioManager(AuditManager):
    def get_queryset(self):
        return ServicioQuerySet(self.model, using=self._db)

    def with_disponibilidad(self):
        return self.get_queryset().with_disponibilidad()

    def prefetch_imagenes(self):
        return self.get_queryset().prefetch_imagenes()
    
    def prefetch_cover(self):
        return self.get_queryset().prefetch_cover()