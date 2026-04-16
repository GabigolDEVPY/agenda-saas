from django import forms
from .models import Establishment
import re


class EstablishmentForm(forms.ModelForm):

    class Meta:
        model = Establishment
        fields = [
            "user",
            "name",
            "cnpj",
            "phone",
            "description",
        ]

    # 🔹 VALIDAR TELEFONE
    def clean_phone(self):
        print("Validando telefone...")
        phone = self.cleaned_data.get("phone")

        if not phone:
            print("Telefone é obrigatório.")
            raise forms.ValidationError("Telefone é obrigatório.")

        phone = re.sub(r"\D", "", phone)

        if len(phone) not in [10, 11]:
            print("Telefone deve ter 10 ou 11 dígitos (DDD + número).")
            raise forms.ValidationError("Telefone inválido. Use DDD + número.")

        # opcional: validar DDD não começar com 0
        if phone[:2] == "00":
            print("DDD não pode começar com 0.")
            raise forms.ValidationError("DDD inválido.")

        return phone

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")

        if not cnpj:
            raise forms.ValidationError("CNPJ é obrigatório.")

        cnpj = re.sub(r"\D", "", cnpj)

        if len(cnpj) != 14:
            raise forms.ValidationError("CNPJ deve ter 14 dígitos.")

        if cnpj == cnpj[0] * 14:
            print("CNPJ com todos os dígitos iguais é inválido.")
            raise forms.ValidationError("CNPJ inválido.")

        if not self.validar_cnpj(cnpj):
            print("CNPJ falhou na validação de dígitos verificadores.")
            raise forms.ValidationError("CNPJ inválido.")

        return cnpj

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