from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ServicioRealizadoProducto


@receiver(post_save, sender=ServicioRealizadoProducto)
def lote_update_consumido_on_servicio_realizado_producto_save(
    sender, instance: ServicioRealizadoProducto, **kwargs
):
    if instance.lote.servicios_restantes == 0:
        instance.lote.consumido = True
        instance.lote.save()
