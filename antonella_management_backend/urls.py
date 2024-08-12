from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, re_path, include
from rest_framework.documentation import include_docs_urls
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("customers/", include("customers.urls")),
    path("inventario/", include("inventory.urls")),
    path("parameters/", include("parameters.urls")),
    path("services/", include("services.urls")),
    path("staff/", include("staff.urls")),
    path("users/", include("users.urls")),
    path("docs/", include_docs_urls(title="Antonella API")),
    path("core", include("core.urls")),
    # Redirigir la raíz al prefijo de la aplicación Angular
    path("", RedirectView.as_view(url="/app/", permanent=True)),
    # Ruta para servir el archivo index.html de Angular
    path("app/", TemplateView.as_view(template_name="index.html")),
]

if settings.DEBUG and settings.USE_LOCAL_STORAGE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static("app", document_root=settings.FRONTEND_ROOT)
urlpatterns += [
    path("app/<path:resource>", TemplateView.as_view(template_name="index.html")),
]
