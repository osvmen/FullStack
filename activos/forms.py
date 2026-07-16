from django import forms

from .models import Activo


class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        fields = [
            "tipo",
            "nombre",
            "empresa",
            "estado",
            "encargado",
            "empresa_responsable",
            "estado_pago",
            "vencimiento",
        ]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "empresa": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "encargado": forms.TextInput(attrs={"class": "form-control"}),
            "empresa_responsable": forms.TextInput(attrs={"class": "form-control"}),
            "estado_pago": forms.Select(attrs={"class": "form-select"}),
            "vencimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
