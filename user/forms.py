from django.contrib.auth.forms import UserCreationForm
from .models import User
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