from django.db import models
from django.utils import timezone


class AuditQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)
    
    def inactive(self):
        return self.filter(deleted_at__isnull=False)


class AuditManager(models.Manager):
    def get_queryset(self):
        return AuditQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()
    
    def inactive(self):
        return self.get_queryset().inactive()


class AuditModel(models.Model):
    created_by = models.CharField(max_length=25, default="root", editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = models.CharField(max_length=25, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    deleted_by = models.CharField(max_length=25, blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        get_latest_by = "created_at"

    objects = AuditManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    def is_deleted(self):
        return self.deleted_at is not None
