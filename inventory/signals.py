from django.utils import timezone
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models import Sum

from services.models import ServicioRealizadoProducto
from .models import ProductoImg, Lote
import os


@receiver(post_delete, sender=ProductoImg)
def eliminar_imagen(sender, instance, **kwargs):
    if instance.imagen and instance.imagen.name:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)


@receiver([post_save, post_delete], sender=Lote)
def producto_update_posee_existencias_on_lote_save(
    sender, instance: Lote, **kwargs
):
    lotes_no_consumidos = (
        Lote.objects.active()
        .filter(producto=instance.producto, consumido=False, fe_exp__gt=timezone.now())
        .all()
    )

    instance.producto.posee_existencias = bool(lotes_no_consumidos)
    instance.producto.save()
