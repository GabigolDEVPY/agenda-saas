from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from .models import User
from .forms import UserCreationForm


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("user:login")


class UserLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'establishment') and user.establishment:
            return reverse(
                "establishment:public_agenda",
                kwargs={"uid": user.establishment.uid}
            )
        return reverse("user:login")


class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("user:login")