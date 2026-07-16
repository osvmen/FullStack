# Gestor de Dominios y Hosting

Sistema simple en Django para registrar y controlar el vencimiento de dominios y
hosting de tus clientes/empresas.

## Datos que gestiona

- Tipo (Dominio o Hosting)
- Nombre
- Empresa
- Estado (Habilitado / Deshabilitado)
- Encargado
- Empresa Responsable
- Estado de Pago (Pagado / Pendiente)
- Vencimiento (fecha)

## Alertas de vencimiento

- **En la interfaz**: al entrar al listado aparece un banner rojo con los
  registros ya **vencidos** y uno amarillo con los que **vencen en los
  próximos 30 días**. Cada fila se resalta en color según su estado
  (`activos/models.py` define `esta_vencido` / `esta_por_vencer`, ajustable
  con `Activo.DIAS_ALERTA`).
- **Por correo**: el comando `python manage.py enviar_alertas_vencimiento`
  recorre todos los registros vencidos o próximos a vencer y envía un email
  por cada uno a la dirección configurada en `ALERTA_EMAIL_DESTINO`. Pensado
  para ejecutarse una vez por día con un scheduler/cron (ver sección de
  despliegue). Si no se configura `ALERTA_EMAIL_DESTINO`, el comando solo
  imprime las alertas en la consola (útil para probar).

## Requisitos

- Python 3.11+

## Instalación local (base de datos SQLite local)

```bash
python3 -m venv venv
source venv/bin/activate           # en Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # crea tu usuario para iniciar sesión
python manage.py runserver
```

Abrí `http://127.0.0.1:8000/` — te va a pedir login (usuario creado arriba) y
después vas a ver el listado. Desde ahí podés cargar, editar y eliminar
registros. También existe el panel de administración estándar de Django en
`/admin/`.

Para probar el envío de alertas por consola:

```bash
python manage.py enviar_alertas_vencimiento
```

## Despliegue gratuito en la nube (Render.com)

El proyecto ya incluye `Procfile`, `render.yaml` y soporte para variables de
entorno, listo para Render (tiene plan gratuito, sin tarjeta de crédito).

1. Subí este repositorio a GitHub (si no lo está ya).
2. Entrá a https://render.com y creá una cuenta gratuita (podés registrarte
   con tu cuenta de GitHub).
3. Click en **New +** → **Blueprint**, y seleccioná este repositorio. Render
   va a detectar el archivo `render.yaml` y va a proponer crear el servicio
   web automáticamente (usa `pip install`, `collectstatic` y `migrate` en el
   build, y `gunicorn` para levantar la app).
   - Si preferís crearlo a mano: **New +** → **Web Service**, elegí el repo,
     Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`,
     Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
4. Configurá las variables de entorno (Render ya genera `SECRET_KEY` solo si
   usás el Blueprint):
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.onrender.com`
   - (opcional, para alertas por email) `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`,
     `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `ALERTA_EMAIL_DESTINO`.
5. Una vez desplegado, entrá a la URL que te da Render y creá el
   superusuario ejecutándolo desde la shell de Render (**Shell** tab):
   `python manage.py createsuperuser`.

### Nota sobre la base de datos en Render (plan free)

El plan gratuito de Render usa disco efímero: si usás SQLite tal cual, los
datos se pueden perder en cada redeploy. Para pruebas cortas no es un
problema, pero si querés persistencia real hay dos opciones simples:

- Crear una base **PostgreSQL free** en Render y setear la variable
  `DATABASE_URL` que Render te da automáticamente al vincular la base — el
  proyecto ya usa `dj-database-url` y la toma sola sin tocar código.
- O desplegar en **PythonAnywhere** (plan free), que sí mantiene el disco
  (y por lo tanto `db.sqlite3`) persistente entre reinicios. Los pasos son
  similares: subir el código, crear un virtualenv, `pip install -r
  requirements.txt`, `python manage.py migrate`, y configurar la app web
  WSGI apuntando a `config.wsgi.application`.

### Alertas automáticas por email en producción (100% gratis)

Render free no tiene Cron Jobs ni Shell, así que la automatización se hace
con un endpoint HTTP protegido por token + un cron externo gratuito:

1. **Configurá el envío de email** en las variables de entorno del servicio
   (Environment):
   - `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
   - `EMAIL_HOST=smtp.gmail.com` (o el SMTP que uses)
   - `EMAIL_PORT=587`
   - `EMAIL_USE_TLS=True`
   - `EMAIL_HOST_USER=tu-correo@gmail.com`
   - `EMAIL_HOST_PASSWORD=` una **contraseña de aplicación** de Gmail (no tu
     contraseña normal — se genera en https://myaccount.google.com/apppasswords,
     requiere verificación en 2 pasos activada)
   - `DEFAULT_FROM_EMAIL=tu-correo@gmail.com`
   - `ALERTA_EMAIL_DESTINO=` el correo que va a recibir las alertas
   - `ALERTA_CRON_TOKEN=` un valor secreto inventado por vos
2. Guardá los cambios (esto redespliega el servicio).
3. La vista `GET /activos/tareas/alertas/?token=TU_TOKEN` ejecuta
   `enviar_alertas_vencimiento` y devuelve `200 OK` si el token es correcto,
   o `403` si falta o es incorrecto. Probala primero manualmente en el navegador.
4. Registrate gratis en https://cron-job.org y creá un cron job que pegue
   diariamente a: `https://TU-APP.onrender.com/activos/tareas/alertas/?token=TU_TOKEN`

**Nota**: el plan free de Render "duerme" el servicio tras ~15 min sin
tráfico y tarda unos segundos en despertar. Configurá el cron con timeout
de al menos 60 segundos si la herramienta lo permite.

## Estructura del proyecto

```
config/            # settings, urls, wsgi del proyecto Django
activos/           # app principal (modelo Activo, vistas, formularios, admin)
  management/commands/enviar_alertas_vencimiento.py
templates/          # templates (Bootstrap 5 vía CDN)
```
