from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings

from activos.models import Activo


class Command(BaseCommand):
    help = (
        "Envia un correo de alerta por cada Dominio/Hosting vencido o "
        "proximo a vencer (dentro de Activo.DIAS_ALERTA dias). "
        "Pensado para ejecutarse a diario mediante un cron/scheduler."
    )

    def handle(self, *args, **options):
        activos = Activo.objects.all()
        alertas = [a for a in activos if a.esta_por_vencer or a.esta_vencido]

        if not alertas:
            self.stdout.write(self.style.SUCCESS("No hay vencimientos pendientes."))
            return

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
            destinatario = getattr(settings, "ALERTA_EMAIL_DESTINO", None)
            if not destinatario:
                self.stdout.write(self.style.WARNING(mensaje))
                continue
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [destinatario],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Alerta enviada: {activo.nombre}"))

        self.stdout.write(
            self.style.SUCCESS(f"Total de alertas procesadas: {len(alertas)}")
        )
