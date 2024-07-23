from django.core.management.base import BaseCommand
from media.models import MediaFile
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Clear temporary media files"

    def handle(self, *args, **kwargs):
        temp_files = MediaFile.objects.filter(
            is_temp=True, uploaded_at__lt=datetime.now()
        )

        if temp_files.count() == 0:
            self.stdout.write(self.style.WARNING("No temporary media files found"))
            return

        for temp_file in temp_files:
            if os.path.isfile(temp_file.file.path):
                os.remove(temp_file.file.path)
            temp_file.delete()

        self.stdout.write(
            self.style.SUCCESS("Successfully cleared temporary media files")
        )
