from .models import AuditModel


class ExcludeAbstractFieldsMixin:
    def get_fields(self):
        fields = super().get_fields()
        audit_fields = AuditModel._meta.get_fields()
        for audit_field in audit_fields:
            if audit_field.name in fields:
                fields.pop(audit_field.name, None)
        return fields
