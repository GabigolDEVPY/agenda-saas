from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import UserCreationForm

class UserLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        uid = getattr(getattr(request.user, "establishment", None), "uid", None)
        if not uid:
            uid = request.session.get("uid")
        logout(request)
        if uid:
            return redirect("establishment:public_agenda", uid=uid)
        return redirect("users:login")
    

class UserLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        return reverse("servicos:home")  # ou qualquer outra página que queira redirecionar após o login

class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("users:login")  # para onde vai depois do registro
