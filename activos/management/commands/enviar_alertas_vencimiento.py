import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from activos.models import Activo


class Command(BaseCommand):
    help = (
        "Envia un correo de alerta por cada Dominio/Hosting vencido o "
        "proximo a vencer (dentro de Activo.DIAS_ALERTA dias), usando la "
        "API HTTP de Resend (no SMTP, que Render bloquea en el plan free). "
        "Pensado para ejecutarse a diario mediante un cron/scheduler."
    )

    def enviar_email(self, asunto, mensaje, destinatario):
        api_key = settings.RESEND_API_KEY
        if not api_key:
            self.stdout.write(self.style.WARNING(mensaje))
            return

        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [destinatario],
                "subject": asunto,
                "text": mensaje,
            },
            timeout=15,
        )
        if not response.ok:
            raise RuntimeError(
                f"Resend devolvió {response.status_code}: {response.text}"
            )

    def handle(self, *args, **options):
        activos = Activo.objects.all()
        alertas = [a for a in activos if a.esta_por_vencer or a.esta_vencido]

        if not alertas:
            self.stdout.write(self.style.SUCCESS("No hay vencimientos pendientes."))
            return

        destinatario = settings.ALERTA_EMAIL_DESTINO

        for activo in alertas:
            estado = "VENCIDO" if activo.esta_vencido else "PRÓXIMO A VENCER"
            asunto = f"[Alerta] {activo.nombre} - {estado}"
            mensaje = (
                f"El {activo.get_tipo_display()} '{activo.nombre}' de la empresa "
                f"{activo.empresa} está {estado.lower()}.\n\n"
                f"Encargado: {activo.encargado}\n"
                f"Empresa responsable: {activo.empresa_responsable}\n"
                f"Estado de pago: {activo.get_estado_pago_display()}\n"
                f"Fecha de vencimiento: {activo.vencimiento.strftime('%d/%m/%Y')}\n"
                f"Días restantes: {activo.dias_restantes}\n"
            )
            if not destinatario:
                self.stdout.write(self.style.WARNING(mensaje))
                continue
            self.enviar_email(asunto, mensaje, destinatario)
            self.stdout.write(self.style.SUCCESS(f"Alerta enviada: {activo.nombre}"))

        self.stdout.write(
            self.style.SUCCESS(f"Total de alertas procesadas: {len(alertas)}")
        )
