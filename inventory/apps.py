import uuid
from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"

    """ def ready(self) -> None:
        from . import signals
        from .models import Lote, ProductoImg

        post_delete.connect(
            signals.eliminar_imagen,
            sender=ProductoImg,
            dispatch_uid=str(uuid.uuid3(uuid.NAMESPACE_OID, "eliminar_imagen")),
        )

        post_save.connect(
            signals.producto_update_posee_existencias_on_lote_save,
            sender=Lote,
            dispatch_uid=str(
                uuid.uuid3(
                    uuid.NAMESPACE_OID, "producto_update_posee_existencias_on_lote_save"
                )
            ),
        )

        post_delete.connect(
            signals.producto_update_posee_existencias_on_lote_save,
            sender=Lote,
            dispatch_uid=str(
                uuid.uuid3(
                    uuid.NAMESPACE_OID, "producto_update_posee_existencias_on_lote_save"
                )
            ),
        ) """
