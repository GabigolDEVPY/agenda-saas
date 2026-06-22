from django import forms
from .models import Establishment, Address
import re


class EstablishmentForm(forms.ModelForm):
    class Meta:
        model = Establishment
        fields = [
            "name",
            "phone",
        ]

    def _only_digits(self, value):
        return re.sub(r"\D", "", value or "")

    def _format_phone(self, phone_digits):
        # 10: (99) 9999-9999 | 11: (99) 99999-9999
        if len(phone_digits) == 10:
            return f"({phone_digits[:2]}) {phone_digits[2:6]}-{phone_digits[6:]}"
        return f"({phone_digits[:2]}) {phone_digits[2:7]}-{phone_digits[7:]}"



    def clean_phone(self):
        phone = self._only_digits(self.cleaned_data.get("phone"))

        if not phone:
            raise forms.ValidationError("Telefone é obrigatório.")

        if len(phone) not in [10, 11]:
            raise forms.ValidationError("Telefone inválido. Use DDD + número.")

        if phone[:2].startswith("0"):
            raise forms.ValidationError("DDD inválido.")

        # Salva mascarado no banco
        return self._format_phone(phone)





class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "zip_code",
            "city",
            "state",
            "neighborhood",
            "street",
            "number",
        ]
        labels = {
            "zip_code": "CEP",
            "city": "Cidade",
            "state": "Estado",
            "neighborhood": "Bairro",
            "street": "Rua / Avenida",
            "number": "Número",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def _only_digits(self, value):
        return re.sub(r"\D", "", value or "")

    def clean_zip_code(self):
        cep = self._only_digits(self.cleaned_data.get("zip_code"))
        if len(cep) != 8:
            raise forms.ValidationError("CEP inválido. Use 8 dígitos.")
        return f"{cep[:5]}-{cep[5:]}"

    def clean_state(self):
        state = (self.cleaned_data.get("state") or "").strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise forms.ValidationError("Estado inválido. Use a UF com 2 letras (ex: SP).")
        return state




class OperatingHoursForm(forms.Form):
    type = forms.CharField()
    day = forms.CharField()
    abertura = forms.TimeField(required=False)
    fechamento = forms.TimeField(required=False)

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("type") == "update_time":
            if not cleaned.get("abertura") or not cleaned.get("fechamento"):
                raise forms.ValidationError("Horários são obrigatórios")

            if cleaned["abertura"] >= cleaned["fechamento"]:
                raise forms.ValidationError("Horário inválido")

        return cleaned
    

