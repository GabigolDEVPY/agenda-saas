from django import forms
from .models import Establishment
import re


class EstablishmentForm(forms.ModelForm):
    class Meta:
        model = Establishment
        fields = [
            "name",
            "cnpj",
            "phone",
            "description",
        ]

    def _only_digits(self, value):
        return re.sub(r"\D", "", value or "")

    def _format_phone(self, phone_digits):
        # 10: (99) 9999-9999 | 11: (99) 99999-9999
        if len(phone_digits) == 10:
            return f"({phone_digits[:2]}) {phone_digits[2:6]}-{phone_digits[6:]}"
        return f"({phone_digits[:2]}) {phone_digits[2:7]}-{phone_digits[7:]}"

    def _format_cnpj(self, cnpj_digits):
        # 00.000.000/0000-00
        return (
            f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/"
            f"{cnpj_digits[8:12]}-{cnpj_digits[12:]}"
        )

    def clean_phone(self):
        print("Validando telefone...")
        phone = self._only_digits(self.cleaned_data.get("phone"))

        if not phone:
            raise forms.ValidationError("Telefone é obrigatório.")

        if len(phone) not in [10, 11]:
            raise forms.ValidationError("Telefone inválido. Use DDD + número.")

        if phone[:2].startswith("0"):
            raise forms.ValidationError("DDD inválido.")

        # Salva mascarado no banco
        return self._format_phone(phone)

    def clean_cnpj(self):
        cnpj = self._only_digits(self.cleaned_data.get("cnpj"))

        if not cnpj:
            raise forms.ValidationError("CNPJ é obrigatório.")

        if len(cnpj) != 14:
            raise forms.ValidationError("CNPJ deve ter 14 dígitos.")

        if cnpj == cnpj[0] * 14:
            raise forms.ValidationError("CNPJ inválido.")

        if not self.validar_cnpj(cnpj):
            raise forms.ValidationError("CNPJ inválido.")

        # Salva mascarado no banco
        return self._format_cnpj(cnpj)

    def validar_cnpj(self, cnpj):
        def calcular_digito(cnpj_parcial, pesos):
            soma = sum(int(digito) * peso for digito, peso in zip(cnpj_parcial, pesos))
            resto = soma % 11
            return "0" if resto < 2 else str(11 - resto)

        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos_2 = [6] + pesos_1

        digito1 = calcular_digito(cnpj[:12], pesos_1)
        digito2 = calcular_digito(cnpj[:12] + digito1, pesos_2)

        return cnpj[-2:] == digito1 + digito2