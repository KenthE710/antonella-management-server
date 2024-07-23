from django.db import models
from os import path


class MediaFile(models.Model):
    file = models.FileField(upload_to=path.join("static", "img", "media", ""))
    is_temp = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
