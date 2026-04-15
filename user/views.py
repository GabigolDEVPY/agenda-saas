from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from .models import User
from .forms import CustomUserCreationForm


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("user:login")


class UserLoginView(LoginView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session['uid'] = None  # Limpa o UID da sessão ao fazer login
        context["hide_navbar"] = True
        return context
    

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'owned_establishment') and user.owned_establishment:
            id = user.owned_establishment.uid
            self.request.session['uid'] = id

            return reverse(
                "establishment:public_agenda",
                kwargs={"uid": user.owned_establishment.uid}
            )
        return reverse("services:home")


class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("user:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_navbar"] = True
        return context