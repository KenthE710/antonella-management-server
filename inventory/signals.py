import os
from django.dispatch import receiver
from django.db.models.signals import post_delete

from .models import ProductoImg


@receiver(post_delete, sender=ProductoImg)
def eliminar_imagen(sender, instance, **kwargs):
    if instance.imagen and instance.imagen.name:
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)
