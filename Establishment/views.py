import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import UpdateView
from .services import HomeService
from .models import Establishment, Address
from .exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from .forms import EstablishmentForm, AddressForm, build_operating_hours_formset


class PublicAgenda(View):
    def get(self, request, uid):
        try:
            context = HomeService.get_context_establishment(uid)
            request.session["uid"] = uid
        except EstablishmentNotFound:
            context = {"msg": "Estabelecimento nao encontrado. Verifique o link ou entre em contato com o estabelecimento para mais informacoes."}
            return render(request, "unavailable.html", context=context)

        except EstablishmentIncomplete:
            context = {"msg": "Configuracoes incompletas. Entre em contato com o estabelecimento para mais informacoes.", "incomplete": True}
            return render(request, "unavailable.html", context=context)

        except EstablishmentInactive:
            context = {"msg": "Estabelecimento inativo. Entre em contato com o estabelecimento para mais informacoes.", "payment": True}
            return render(request, "unavailable.html", context=context)

        return render(request, "home.html", context=context)


class EstablishmentOwnerRequiredMixin(LoginRequiredMixin):
    def get_establishment(self):
        uid = self.request.session.get("uid")
        if not uid:
            raise PermissionDenied("Sessao sem estabelecimento selecionado.")

        return get_object_or_404(Establishment, uid=uid, user=self.request.user)

    def _build_error_message(self, form_or_formset):
        mensagens = []

        if hasattr(form_or_formset, "non_form_errors"):
            mensagens.extend([str(err) for err in form_or_formset.non_form_errors()])

        if hasattr(form_or_formset, "forms"):
            for form in form_or_formset.forms:
                for field, errors in form.errors.items():
                    if field == "__all__":
                        mensagens.extend([str(err) for err in errors])
                    else:
                        label = form.fields[field].label or field
                        mensagens.extend([f"{label}: {err}" for err in errors])
        else:
            for field, errors in form_or_formset.errors.items():
                if field == "__all__":
                    mensagens.extend([str(err) for err in errors])
                else:
                    label = form_or_formset.fields[field].label or field
                    mensagens.extend([f"{label}: {err}" for err in errors])

        return " | ".join(mensagens) if mensagens else "Verifique os dados do formulario."


def order_operating_hours_forms(formset):
    order_map = {6: 0, 0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6}

    def _day(form):
        try:
            return int(form["day_of_week"].value())
        except (TypeError, ValueError):
            return 99

    return sorted(formset.forms, key=lambda form: order_map.get(_day(form), 99))


class SaveInfosView(EstablishmentOwnerRequiredMixin, UpdateView):
    model = Establishment
    form_class = EstablishmentForm
    template_name = "partials/infos.html"

    def get_object(self, queryset=None):
        return self.get_establishment()

    def form_valid(self, form):
        self.object = form.save()

        response = render(
            self.request,
            self.template_name,
            {"establishment": self.object, "form": form},
        )
        response["HX-Trigger"] = json.dumps(
            {
                "notify": {
                    "type": "success",
                    "message": "Informacoes salvas com sucesso!",
                }
            }
        )
        return response

    def form_invalid(self, form):
        self.object = self.get_object()

        response = render(
            self.request,
            self.template_name,
            {"establishment": self.object, "form": form},
            status=400,
        )
        response["HX-Trigger"] = json.dumps(
            {
                "notify": {
                    "type": "error",
                    "message": self._build_error_message(form),
                }
            }
        )
        return response


class SaveAddressView(EstablishmentOwnerRequiredMixin, View):
    template_name = "partials/address.html"

    def post(self, request, *args, **kwargs):
        establishment = self.get_establishment()
        address_instance = Address.objects.filter(establishment=establishment).first()

        form = AddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            address = form.save(commit=False)
            address.establishment = establishment
            address.save()

            response = render(
                request,
                self.template_name,
                {"establishment": establishment, "address": address, "form": form},
            )
            response["HX-Trigger"] = json.dumps(
                {
                    "notify": {
                        "type": "success",
                        "message": "Endereco salvo com sucesso!",
                    }
                }
            )
            return response

        response = render(
            request,
            self.template_name,
            {"establishment": establishment, "address": address_instance, "form": form},
            status=400,
        )
        response["HX-Trigger"] = json.dumps(
            {
                "notify": {
                    "type": "error",
                    "message": self._build_error_message(form),
                }
            }
        )
        return response


class SaveOperatingHoursView(EstablishmentOwnerRequiredMixin, View):
    template_name = "partials/operating_hours.html"

    def post(self, request, *args, **kwargs):
        establishment = self.get_establishment()
        formset = build_operating_hours_formset(establishment=establishment, data=request.POST)

        if formset.is_valid():
            for form in formset.forms:
                if not form.cleaned_data:
                    continue

                operating_hours = form.save(commit=False)
                operating_hours.establishment = establishment
                operating_hours.save()

            refreshed_formset = build_operating_hours_formset(establishment=establishment)
            response = render(
                request,
                self.template_name,
                {
                    "establishment": establishment,
                    "operating_hours_formset": refreshed_formset,
                    "operating_hours_forms": order_operating_hours_forms(refreshed_formset),
                },
            )
            response["HX-Trigger"] = json.dumps(
                {
                    "notify": {
                        "type": "success",
                        "message": "Horarios de funcionamento salvos com sucesso!",
                    }
                }
            )
            return response

        response = render(
            request,
            self.template_name,
            {
                "establishment": establishment,
                "operating_hours_formset": formset,
                "operating_hours_forms": order_operating_hours_forms(formset),
            },
            status=400,
        )
        response["HX-Trigger"] = json.dumps(
            {
                "notify": {
                    "type": "error",
                    "message": self._build_error_message(formset),
                }
            }
        )
        return response
