from core.models import AuditManager
from .querysets import ProductoQuerySet, LoteQuerySet


class ProductoManager(AuditManager):
    def get_queryset(self):
        return ProductoQuerySet(self.model, using=self._db)

    def with_posee_existencias(self):
        return self.get_queryset().with_posee_existencias()
    
    def with_existencias(self):
        return self.get_queryset().with_existencias()

class LoteManager(AuditManager):
    def get_queryset(self):
        return LoteQuerySet(self.model, using=self._db)
    
    def with_servicios_restantes(self):
        return self.get_queryset().with_servicios_restantes()