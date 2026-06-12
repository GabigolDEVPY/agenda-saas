import json
from establishment.models import Establishment, Address, OperatingHours, GeneralPreference
from services.services import ServiceService
from user.forms import EmployeeCreationForm
from user.models import Preferences
from appointment.models import MonthAvailability, HoursUnavailable
import datetime


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
        context['services'] = ServiceService.get_services(
            view.request.user,
            service_users=context['service_users'],
        )
        context['service_form'] = ServiceService.get_form(
            view.request.user,
            users=context['service_users'],
        )

        hours = HoursUnavailable.objects.filter(user=view.request.user).select_related('month')
        dias_off = []
        horarios = {}
        
        for h in hours:
            # h.month.month is 0-indexed in DB, but frontend expects 1-indexed for date strings
            date_str = f"{h.month.year}-{h.month.month:02d}-{h.day:02d}"
            if h.hour == datetime.time(0, 0):
                dias_off.append(date_str)
            else:
                if date_str not in horarios:
                    horarios[date_str] = []
                slot_str = h.hour.strftime('%H:%M')
                horarios[date_str].append(slot_str)
        
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
