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
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["uid"] = self.request.user.establishment.uid
        return response


    def get_success_url(self):
        uid = self.request.session.get("uid")
        if uid:
            return reverse("establishment:public_agenda", kwargs={"uid": uid})
        return reverse("users:login")  # fallback, caso algo dê errado

class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("users:login")  # para onde vai depois do registro
