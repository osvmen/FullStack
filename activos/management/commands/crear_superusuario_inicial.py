import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Crea un superusuario inicial a partir de las variables de entorno "
        "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL y "
        "DJANGO_SUPERUSER_PASSWORD, si todavia no existe. Pensado para "
        "correr en el build de plataformas sin acceso a shell (plan free "
        "de Render)."
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USERNAME/PASSWORD no configurados, "
                    "se omite la creacion del superusuario."
                )
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f"El usuario '{username}' ya existe, no se crea de nuevo.")
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado correctamente."))
