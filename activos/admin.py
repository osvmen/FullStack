from django.contrib import admin

from .models import Activo


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo",
        "empresa",
        "estado",
        "encargado",
        "empresa_responsable",
        "estado_pago",
        "vencimiento",
    )
    list_filter = ("tipo", "estado", "estado_pago")
    search_fields = ("nombre", "empresa", "encargado", "empresa_responsable")
