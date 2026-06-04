from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from .models import Preferences, User
from django import forms


class CustomUserCreationForm(UserCreationForm):
    establishment_name = forms.CharField(
        label="Nome do Estabelecimento",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=30
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "establishment_name"]
        widgets = {
            "username":   forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "email":      forms.EmailInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_owner = True

        if commit:
            user.save()

            from establishment.models import Establishment
            establishment = Establishment.objects.create(
                user=user,
                name=self.cleaned_data["establishment_name"]
            )
            user.establishment = establishment
            user.save()

        return user


class ProfileDisplayNameForm(forms.Form):
    display_name = forms.CharField(max_length=150, required=True)

    def clean_display_name(self):
        display_name = (self.cleaned_data.get("display_name") or "").strip()
        if not display_name:
            raise forms.ValidationError("Informe um nome de exibicao.")
        return " ".join(display_name.split())


class MaxAppointmentsForm(forms.ModelForm):
    class Meta:
        model = Preferences
        fields = ["max_appointments"]

    def clean_max_appointments(self):
        max_appointments = self.cleaned_data.get("max_appointments")
        if max_appointments is None or max_appointments < 1:
            raise forms.ValidationError("Use pelo menos 1 agendamento por dia.")
        return max_appointments


class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_owner = False
        if commit:
            user.save()
        return user


class EmployeePasswordChangeForm(SetPasswordForm):
    pass

