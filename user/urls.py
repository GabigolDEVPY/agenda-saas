from django.urls import path
from .views import (
    ChangeConfirmManuallyAppointmentsView,
    ChangeMaxAppointmentsView,
    ChangeNameView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    EmployeeCreateView,
)

app_name = "user"

urlpatterns = [
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),

    # create employees and edit
    path("create-employee/", EmployeeCreateView.as_view(), name="create_employee"),

    path("change-name/", ChangeNameView.as_view(), name="change_name"),
    path("change-max-appointments/", ChangeMaxAppointmentsView.as_view(), name="change_max_appointments"),
    path("change-confirm-manually-appointments/",ChangeConfirmManuallyAppointmentsView.as_view(),name="change_confirm_manually_appointments"),
    
]
