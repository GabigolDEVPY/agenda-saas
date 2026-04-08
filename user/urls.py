from django.urls import path
from .views import UserLogoutView, UserLoginView, UserRegisterView

app_name = "user"

urlpatterns = [
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
]