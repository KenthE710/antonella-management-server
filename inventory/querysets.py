from django.utils import timezone
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import (
    OuterRef,
    Subquery,
    Sum,
    F,
    IntegerField,
    ExpressionWrapper,
    Case,
    When,
    Exists,
    BooleanField
)

from core.models import AuditQuerySet


class LoteQuerySet(AuditQuerySet):
    def with_servicios_restantes(self):
        from services.models import ServicioRealizadoProducto

        servicios_realizados_subquery = (
            ServicioRealizadoProducto.objects.active()
            .filter(lote=OuterRef("pk"))
            .values("lote")
            .annotate(total=Sum("cantidad", default=0))
            .values("total")
        )

        return self.annotate(
            servicios_realizados=Coalesce(
                Subquery(
                    servicios_realizados_subquery,
                    output_field=IntegerField(),
                ),
                0,
            ),
            servicios_restantes=ExpressionWrapper(
                F("producto__usos_est") * F("cant") - F("servicios_realizados"),
                output_field=IntegerField(),
            ),
        )


class ProductoQuerySet(AuditQuerySet):
    def with_posee_existencias(self):
        from .models import Lote

        posee_existencias_subquery = (
            Lote.objects.active()
            .with_servicios_restantes()
            .filter(
                producto=OuterRef("pk"),
                retirado=False,
                fe_exp__gt=timezone.now(),
                servicios_restantes__gt=0,
            )
            .values("producto")
        )

        return self.annotate(
            posee_existencias=Case(
                When(Exists(posee_existencias_subquery), then=True),
                default=False,
                output_field=BooleanField(),
            )
        )

    def with_existencias(self):
        from .models import Lote

        existencias_subquery = (
            Lote.objects.active()
            .filter(producto=OuterRef("pk"), retirado=False, fe_exp__gt=timezone.now())
            .values("producto")
            .annotate(total=Sum("cant", default=0))
            .values("total")
        )

        return self.annotate(
            existencias=Coalesce(
                Subquery(existencias_subquery, output_field=IntegerField()), 0
            )
        )
