from django import forms
from .models import Appointment
import re


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = [
            "employee",
            "service",
            "date",
            "time",
            "client_name",
            "phone",
            "observation",
            "total",
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            raise forms.ValidationError("Telefone é obrigatório.")

        # remove tudo que não for número
        phone = re.sub(r"\D", "", phone)

        # valida tamanho (Brasil)
        if len(phone) not in [10, 11]:
            raise forms.ValidationError("Telefone inválido. Use DDD + número.")

        return phone

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        # exemplo de validação extra útil
        if date and time:
            # você pode validar aqui se o horário já passou, etc
            pass

        return cleaned_data