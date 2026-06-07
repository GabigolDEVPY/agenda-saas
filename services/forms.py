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

    def clean_price(self):
        price = self.cleaned_data.get("price")

        if price is not None and price < 0:
            raise forms.ValidationError("Preco nao pode ser negativo.")

        return price

    def clean_time_duration(self):
        duration = self.cleaned_data.get("time_duration")

        if duration is not None and duration < 10:
            raise forms.ValidationError("Duracao minima de 10 minutos.")

        if duration is not None and duration % 5 != 0:
            raise forms.ValidationError("Duracao deve ser multipla de 5 minutos.")

        return duration
