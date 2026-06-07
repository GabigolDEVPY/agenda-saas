from django import forms

from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["user", "name", "price", "time_duration"]

    def __init__(self, *args, users=None, **kwargs):
        super().__init__(*args, **kwargs)
        if users is not None:
            self.fields["user"].queryset = users

        self.fields["user"].label = "Profissional"
        self.fields["name"].label = "Nome do Servico"
        self.fields["price"].label = "Preco (R$)"
        self.fields["time_duration"].label = "Duracao (minutos)"
        self.fields["price"].widget = forms.NumberInput(attrs={"min": "0", "step": "0.50"})
        self.fields["time_duration"].widget = forms.NumberInput(attrs={"min": "10", "step": "5"})

    def clean_name(self):
        return " ".join((self.cleaned_data.get("name") or "").strip().split())
