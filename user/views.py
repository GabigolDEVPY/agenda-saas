from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.views import View
from .models import Preferences, User
from .forms import CustomUserCreationForm, MaxAppointmentsForm, ProfileDisplayNameForm
from .services.services import UserServices


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
                "client_portal:public_agenda",
                kwargs={"uid": user.owned_establishment.uid}
            )
        return reverse("admin_portal:home")


class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("user:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_navbar"] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        UserServices.create_data_establishment(user)
        return response


class ProfilePartialMixin(LoginRequiredMixin, View):
    template_name = None

    def get_preferences(self):
        preferences, _ = Preferences.objects.get_or_create(user=self.request.user)
        return preferences

    def render_partial(self, form=None):
        return render(
            self.request,
            self.template_name,
            {
                "profile_user": self.request.user,
                "preferences": self.get_preferences(),
                "max_appointment_options": range(1, 31),
                "form": form,
            },
        )


class ChangeNameView(ProfilePartialMixin):
    template_name = "partials/profile/personal_data.html"

    def post(self, request, *args, **kwargs):
        form = ProfileDisplayNameForm(request.POST)

        if form.is_valid():
            display_name = form.cleaned_data["display_name"]
            first_name, _, last_name = display_name.partition(" ")
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save(update_fields=["first_name", "last_name"])
            form = None

        return self.render_partial(form=form)


class ChangeMaxAppointmentsView(ProfilePartialMixin):
    template_name = "partials/profile/max_appointments.html"

    def post(self, request, *args, **kwargs):
        preferences = self.get_preferences()
        form = MaxAppointmentsForm(request.POST, instance=preferences)

        if form.is_valid():
            preferences = form.save()
            form = MaxAppointmentsForm(instance=preferences)

        return self.render_partial(form=form)


class ChangeConfirmManuallyAppointmentsView(ProfilePartialMixin):
    template_name = "partials/profile/confirm_manually_appointments.html"

    def post(self, request, *args, **kwargs):
        preferences = self.get_preferences()
        preferences.confirm_manually_appointments = "confirm_manually_appointments" in request.POST
        preferences.save(update_fields=["confirm_manually_appointments"])
        return self.render_partial()

