import uuid
from django.apps import AppConfig
from django.db.models.signals import post_delete


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"

    def ready(self) -> None:
        from . import signals

        post_delete.connect(
            signals.eliminar_imagen,
            dispatch_uid=str(uuid.uuid3(uuid.NAMESPACE_OID, "eliminar_imagen")),
        )
