from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import UserCreationForm

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("estabilishment")   # para onde vai depois do logout


class UserLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True
    
    def get_success_url(self):
        uid = self.request.session.get("uid")
        if uid:
            return reverse("establishment:public_agenda", kwargs={"uid": uid})
        return reverse("uaser:login")  # fallback, caso algo dê errado

class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("user:login")  # para onde vai depois do registro