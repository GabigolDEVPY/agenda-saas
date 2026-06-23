import json
from django.urls import reverse
from billing.services import LimitsService
from establishment.models import Establishment, Address, OperatingHours, GeneralPreference
from services.services import ServiceService
from user.forms import EmployeeCreationForm
from user.models import Preferences
from appointment.models import MonthAvailability, HoursUnavailable, DayUnavailable
from appointment.services import AppointmentAdminService


class AdminService:
    @staticmethod
    def get_establishment(request):
        establishment = ServiceService.get_establishment(request.user)
        if establishment:
            return establishment

        uid = request.session.get('uid')
        if uid:
            return Establishment.objects.filter(uid=uid).first()

        return None

    @staticmethod
    def get_appointments_by_month(user):
        return AppointmentAdminService.get_confirmed_appointments(user)

    @staticmethod
    def get_portal_link(request, establishment):
        if not establishment:
            return ''
        path = reverse('client_portal:public_agenda', kwargs={'uid': establishment.uid})
        return request.build_absolute_uri(path)
    
    @staticmethod
    def get_context_admin(view, **kwargs):
        context = super(type(view), view).get_context_data(**kwargs)

        establishment = AdminService.get_establishment(view.request)
        general_preferences = None
        if establishment:
            general_preferences, _ = GeneralPreference.objects.get_or_create(establishment=establishment)

        context['establishment'] = establishment
        context['address'] = Address.objects.filter(establishment=establishment).first() if establishment else None
        context['establishment_config_incomplete'] = not context['address'] or not context['address'].completed
        context['operating_hours'] = json.dumps(AdminService.get_operating_hours(view, establishment))
        context['gereral_preferences'] = general_preferences
        context['profile_user'] = view.request.user
        context['preferences'], _ = Preferences.objects.get_or_create(user=view.request.user)
        context['max_appointment_options'] = range(1, 31)
        context['employees'] = establishment.users.filter(is_owner=False).order_by("first_name", "last_name", "username") if establishment else []
        context['employee_form'] = EmployeeCreationForm()
        context['service_users'] = ServiceService.get_service_users(view.request.user, establishment)
        context['services'] = ServiceService.get_services(view.request.user,service_users=context['service_users'],)
        context['service_form'] = ServiceService.get_form(view.request.user,users=context['service_users'],)
        context['limits'] = LimitsService.context(view.request.user, establishment)
        context['billing'] = context['limits']['billing']
        context.update(AppointmentAdminService.appointments_panel_context(view.request.user))
        context['portal_link'] = AdminService.get_portal_link(view.request, establishment)

        hours = HoursUnavailable.objects.filter(user=view.request.user).select_related('month')
        days_off_qs = DayUnavailable.objects.filter(user=view.request.user).select_related('month')
        dias_off = []
        horarios = {}

        for d in days_off_qs:
            date_str = f"{d.month.year}-{d.month.month:02d}-{d.day:02d}"
            dias_off.append(date_str)

        for h in hours:
            date_str = f"{h.month.year}-{h.month.month:02d}-{h.day:02d}"
            if date_str not in horarios:
                horarios[date_str] = []
            horarios[date_str].append(h.hour.strftime('%H:%M'))
        
        context['dias_off_json'] = json.dumps(dias_off)
        context['horarios_json'] = json.dumps(horarios)
        
        months = MonthAvailability.objects.filter(user=view.request.user, availability=True)
        opened_months = [{'y': m.year, 'm': m.month - 1} for m in months]
        context['opened_months_json'] = json.dumps(opened_months)

        return context

    @staticmethod
    def get_service_users(request, establishment):
        return ServiceService.get_service_users(request.user, establishment)

    @staticmethod
    def get_operating_hours(_view, establishment):
        dias_map = {
            0: 'seg',
            1: 'ter',
            2: 'qua',
            3: 'qui',
            4: 'sex',
            5: 'sab',
            6: 'dom',
        }

        defaults = {
            'dom': {'aberto': False, 'abertura': '08:00', 'fechamento': '18:00'},
            'seg': {'aberto': True, 'abertura': '08:00', 'fechamento': '20:00'},
            'ter': {'aberto': True, 'abertura': '08:00', 'fechamento': '20:00'},
            'qua': {'aberto': True, 'abertura': '08:00', 'fechamento': '20:00'},
            'qui': {'aberto': True, 'abertura': '08:00', 'fechamento': '20:00'},
            'sex': {'aberto': True, 'abertura': '08:00', 'fechamento': '20:00'},
            'sab': {'aberto': True, 'abertura': '09:00', 'fechamento': '18:00'},
        }
        if not establishment:
            return defaults

        operating_hours = OperatingHours.objects.filter(establishment=establishment).order_by('day_of_week')
        result = defaults.copy()

        for item in operating_hours:
            key = dias_map.get(item.day_of_week)
            if not key:
                continue

            result[key] = {
                'aberto': not item.is_closed,
                'abertura': item.open_time.strftime('%H:%M'),
                'fechamento': item.close_time.strftime('%H:%M'),
            }

        return result
