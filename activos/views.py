import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import Activo
from .forms import ActivoForm


class ActivoListView(LoginRequiredMixin, ListView):
    model = Activo
    template_name = "activos/activo_list.html"
    context_object_name = "activos"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("q")
        tipo = self.request.GET.get("tipo")
        estado = self.request.GET.get("estado")
        estado_pago = self.request.GET.get("estado_pago")
        alerta = self.request.GET.get("alerta")

        if query:
            qs = qs.filter(
                Q(nombre__icontains=query)
                | Q(empresa__icontains=query)
                | Q(encargado__icontains=query)
                | Q(empresa_responsable__icontains=query)
            )
        if tipo:
            qs = qs.filter(tipo=tipo)
        if estado:
            qs = qs.filter(estado=estado)
        if estado_pago:
            qs = qs.filter(estado_pago=estado_pago)
        if alerta == "vencido":
            ids = [a.id for a in qs if a.esta_vencido]
            qs = qs.filter(id__in=ids)
        elif alerta == "por_vencer":
            ids = [a.id for a in qs if a.esta_por_vencer]
            qs = qs.filter(id__in=ids)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = Activo.objects.all()
        context["total_vencidos"] = sum(1 for a in todos if a.esta_vencido)
        context["total_por_vencer"] = sum(1 for a in todos if a.esta_por_vencer)
        context["filtros"] = self.request.GET
        context["tipos"] = Activo.Tipo.choices
        context["estados"] = Activo.Estado.choices
        context["estados_pago"] = Activo.EstadoPago.choices
        return context


class ActivoCreateView(LoginRequiredMixin, CreateView):
    model = Activo
    form_class = ActivoForm
    template_name = "activos/activo_form.html"
    success_url = reverse_lazy("activos:lista")

    def form_valid(self, form):
        messages.success(self.request, "Registro creado correctamente.")
        return super().form_valid(form)


class ActivoUpdateView(LoginRequiredMixin, UpdateView):
    model = Activo
    form_class = ActivoForm
    template_name = "activos/activo_form.html"
    success_url = reverse_lazy("activos:lista")

    def form_valid(self, form):
        messages.success(self.request, "Registro actualizado correctamente.")
        return super().form_valid(form)


class ActivoDeleteView(LoginRequiredMixin, DeleteView):
    model = Activo
    template_name = "activos/activo_confirm_delete.html"
    success_url = reverse_lazy("activos:lista")

    def form_valid(self, form):
        messages.success(self.request, "Registro eliminado.")
        return super().form_valid(form)


def ejecutar_alertas_vencimiento(request):
    """Dispara el envío de alertas de vencimiento por email.

    Pensado para ser llamado por un cron externo gratuito (Render free no
    tiene Cron Jobs ni Shell), protegido con un token compartido en vez de
    login, porque el llamador no es un usuario con sesión.
    """
    token_esperado = settings.ALERTA_CRON_TOKEN
    token_recibido = request.GET.get("token", "")
    if not token_esperado or not secrets.compare_digest(token_recibido, token_esperado):
        return HttpResponseForbidden("Token inválido o no configurado.")

        try:
        call_command("enviar_alertas_vencimiento")
    except Exception as exc:
        return HttpResponse(f"Error al procesar alertas: {exc}", status=500)

    return HttpResponse("Alertas procesadas correctamente.")
