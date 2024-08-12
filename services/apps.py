import uuid
from django.apps import AppConfig
from django.db.models.signals import post_save


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"

    """ def ready(self) -> None:
        from . import signals
        from .models import ServicioRealizadoProducto

        post_save.connect(
            signals.lote_update_consumido_on_servicio_realizado_producto_save,
            sender=ServicioRealizadoProducto,
            dispatch_uid=str(
                uuid.uuid3(
                    uuid.NAMESPACE_OID,
                    "lote_update_consumido_on_servicio_realizado_producto_save",
                )
            ),
        ) """
