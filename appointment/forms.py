from django import forms
from .models import Appointment
import re


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = [
            "user",
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

        phone = re.sub(r"\D", "", phone)

        if len(phone) not in [10, 11]:
            raise forms.ValidationError("Telefone inválido. Use DDD + número.")

        return phone

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        if date and time:
            pass

        return cleaned_data