from typing import Any
from django.db.models import OuterRef, Case, When, Exists, BooleanField, Prefetch

from core.models import AuditQuerySet


class ServicioQuerySet(AuditQuerySet):
    def with_disponibilidad(self):
        from inventory.models import Producto

        noTieneExistenciasQuery = (
            Producto.objects.active()
            .with_posee_existencias()
            .filter(servicios__id=OuterRef("pk"), posee_existencias=False)
            .values("id")
        )
        return self.annotate(
            disponibilidad=Case(
                When(~Exists(noTieneExistenciasQuery), then=True),
                default=False,
                output_field=BooleanField(),
            )
        )

    def prefetch_imagenes(self):
        from .models import ServicioImg

        return self.prefetch_related(
            Prefetch(
                "imagenes",
                queryset=ServicioImg.objects.active(),
                to_attr="img",
            )
        )

    def prefetch_cover(self):
        from .models import ServicioImg

        return self.prefetch_related(
            Prefetch(
                "imagenes",
                queryset=ServicioImg.objects.active().filter(is_cover=True),
                to_attr="cover",
            )
        )
