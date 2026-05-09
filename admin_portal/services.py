import json
from establishment.models import Establishment, Address, OperatingHours



class AdminService:
    @staticmethod
    def get_context_admin(view, **kwargs):
        context = super(type(view), view).get_context_data(**kwargs)

        uid = view.request.session.get('uid')
        establishment = Establishment.objects.filter(uid=uid).first()

        context['establishment'] = establishment
        context['address'] = Address.objects.filter(establishment=establishment).first() if establishment else None
        context['operating_hours'] = json.dumps(AdminService.get_operating_hours(view, establishment))

        return context

    @staticmethod
    def get_operating_hours(view, establishment):
            dias_map = {0: 'seg',1: 'ter',2: 'qua',3: 'qui',4: 'sex',5: 'sab',6: 'dom',}

            defaults = {
                'dom': {'aberto': False, 'abertura': '08:00', 'fechamento': '18:00'},
                'seg': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'ter': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'qua': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'qui': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'sex': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'sab': {'aberto': True,  'abertura': '09:00', 'fechamento': '18:00'},
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
                    'aberto': not item.is_closed,'abertura': item.open_time.strftime('%H:%M'),'fechamento': item.close_time.strftime('%H:%M'),
                }

            return result
