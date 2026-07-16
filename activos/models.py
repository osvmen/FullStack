from datetime import date

from django.db import models


class Activo(models.Model):
    class Tipo(models.TextChoices):
        DOMINIO = "DOMINIO", "Dominio"
        HOSTING = "HOSTING", "Hosting"

    class Estado(models.TextChoices):
        HABILITADO = "HABILITADO", "Habilitado"
        DESHABILITADO = "DESHABILITADO", "Deshabilitado"

    class EstadoPago(models.TextChoices):
        PAGADO = "PAGADO", "Pagado"
        PENDIENTE = "PENDIENTE", "Pendiente"

    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    nombre = models.CharField(max_length=255)
    empresa = models.CharField(max_length=255)
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.HABILITADO
    )
    encargado = models.CharField(max_length=255)
    empresa_responsable = models.CharField(max_length=255)
    estado_pago = models.CharField(
        max_length=10, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE
    )
    vencimiento = models.DateField()

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    # Días antes del vencimiento en los que se considera "próximo a vencer"
    DIAS_ALERTA = 30

    class Meta:
        ordering = ["vencimiento"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

    @property
    def dias_restantes(self):
        return (self.vencimiento - date.today()).days

    @property
    def esta_vencido(self):
        return self.dias_restantes < 0

    @property
    def esta_por_vencer(self):
        return 0 <= self.dias_restantes <= self.DIAS_ALERTA

    @property
    def estado_vencimiento(self):
        if self.esta_vencido:
            return "vencido"
        if self.esta_por_vencer:
            return "por_vencer"
        return "vigente"
