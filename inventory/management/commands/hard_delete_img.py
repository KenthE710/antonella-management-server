from django.core.management.base import BaseCommand
from django.db.models.manager import BaseManager
from inventory.models import ProductoImg


class Command(BaseCommand):
    help = "Elimina permanente las imágenes dependiendo de los filtros pasados."

    def handle(self, *args, **kwargs):
        imgs: BaseManager[ProductoImg] = (
            ProductoImg.objects.filter(imagen__isnull=False).inactive().all()
        )

        for img in imgs:
            img.hard_delete()

        self.stdout.write(self.style.SUCCESS(f"Se eliminaron las imagenes"))
