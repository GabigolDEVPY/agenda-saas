import re
from django import forms
from django.forms import BaseModelFormSet, modelformset_factory
from .models import Establishment, Address, OperatingHours


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
        if len(phone_digits) == 10:
            return f"({phone_digits[:2]}) {phone_digits[2:6]}-{phone_digits[6:]}"
        return f"({phone_digits[:2]}) {phone_digits[2:7]}-{phone_digits[7:]}"

    def _format_cnpj(self, cnpj_digits):
        return (
            f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/"
            f"{cnpj_digits[8:12]}-{cnpj_digits[12:]}"
        )

    def clean_phone(self):
        phone = self._only_digits(self.cleaned_data.get("phone"))

        if not phone:
            raise forms.ValidationError("Telefone e obrigatorio.")

        if len(phone) not in [10, 11]:
            raise forms.ValidationError("Telefone invalido. Use DDD + numero.")

        if phone[:2].startswith("0"):
            raise forms.ValidationError("DDD invalido.")

        return self._format_phone(phone)

    def clean_cnpj(self):
        cnpj = self._only_digits(self.cleaned_data.get("cnpj"))

        if not cnpj:
            raise forms.ValidationError("CNPJ e obrigatorio.")

        if len(cnpj) != 14:
            raise forms.ValidationError("CNPJ deve ter 14 digitos.")

        if cnpj == cnpj[0] * 14:
            raise forms.ValidationError("CNPJ invalido.")

        if not self.validar_cnpj(cnpj):
            raise forms.ValidationError("CNPJ invalido.")

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
            "complement",
        ]
        labels = {
            "zip_code": "CEP",
            "city": "Cidade",
            "state": "Estado",
            "neighborhood": "Bairro",
            "street": "Rua / Avenida",
            "number": "Numero",
            "complement": "Complemento",
        }

    def _only_digits(self, value):
        return re.sub(r"\D", "", value or "")

    def clean_zip_code(self):
        cep = self._only_digits(self.cleaned_data.get("zip_code"))
        if len(cep) != 8:
            raise forms.ValidationError("CEP invalido. Use 8 digitos.")
        return f"{cep[:5]}-{cep[5:]}"

    def clean_state(self):
        state = (self.cleaned_data.get("state") or "").strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise forms.ValidationError("Estado invalido. Use a UF com 2 letras (ex: SP).")
        return state


class OperatingHoursForm(forms.ModelForm):
    DAY_LABELS = {
        0: "Segunda",
        1: "Terca",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sabado",
        6: "Domingo",
    }
    DEFAULTS_BY_DAY = {
        0: ("08:00", "20:00"),
        1: ("08:00", "20:00"),
        2: ("08:00", "20:00"),
        3: ("08:00", "20:00"),
        4: ("08:00", "20:00"),
        5: ("09:00", "18:00"),
        6: ("08:00", "18:00"),
    }

    class Meta:
        model = OperatingHours
        fields = ["day_of_week", "is_closed", "open_time", "close_time"]
        widgets = {
            "day_of_week": forms.HiddenInput(),
            "open_time": forms.TimeInput(attrs={"type": "time"}),
            "close_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        day_of_week = self.initial.get("day_of_week", self.instance.day_of_week)
        self.day_label = self.DAY_LABELS.get(day_of_week, "Dia")

    def clean(self):
        cleaned_data = super().clean()
        is_closed = cleaned_data.get("is_closed")
        open_time = cleaned_data.get("open_time")
        close_time = cleaned_data.get("close_time")
        day_of_week = cleaned_data.get("day_of_week")

        if is_closed:
            if day_of_week is not None and (open_time is None or close_time is None):
                default_open, default_close = self.DEFAULTS_BY_DAY.get(day_of_week, ("08:00", "18:00"))
                cleaned_data["open_time"] = default_open
                cleaned_data["close_time"] = default_close
            return cleaned_data

        if open_time is None:
            self.add_error("open_time", "Informe o horario de abertura.")

        if close_time is None:
            self.add_error("close_time", "Informe o horario de fechamento.")

        if open_time and close_time and open_time >= close_time:
            self.add_error("close_time", "O horario de fechamento deve ser maior que o de abertura.")

        return cleaned_data


class BaseOperatingHoursFormSet(BaseModelFormSet):
    REQUIRED_DAYS = {0, 1, 2, 3, 4, 5, 6}

    def clean(self):
        super().clean()
        seen_days = set()

        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue

            day = form.cleaned_data.get("day_of_week")
            if day is None:
                continue

            if day in seen_days:
                raise forms.ValidationError("Cada dia da semana deve aparecer apenas uma vez.")

            seen_days.add(day)

        missing_days = self.REQUIRED_DAYS - seen_days
        if missing_days:
            raise forms.ValidationError("Todos os dias da semana precisam ser enviados no formulario.")


def build_operating_hours_formset(establishment, data=None):
    queryset = OperatingHours.objects.filter(establishment=establishment).order_by("day_of_week")
    existing_by_day = {item.day_of_week: item for item in queryset}

    initial = []
    for day in range(7):
        if day in existing_by_day:
            continue

        default_open, default_close = OperatingHoursForm.DEFAULTS_BY_DAY.get(day, ("08:00", "18:00"))
        initial.append(
            {
                "day_of_week": day,
                "open_time": default_open,
                "close_time": default_close,
                "is_closed": day == 6,
            }
        )

    OperatingHoursFormSet = modelformset_factory(
        OperatingHours,
        form=OperatingHoursForm,
        formset=BaseOperatingHoursFormSet,
        extra=len(initial),
        can_delete=False,
    )

    return OperatingHoursFormSet(
        data=data,
        queryset=queryset,
        initial=initial,
        prefix="operating_hours",
    )
