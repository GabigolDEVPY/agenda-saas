import json
from establishment.models import OperatingHours

class OperationDayService:
    @staticmethod
    def update_operating_hours(day, user, establishment, type="update_day"):
        if not user.is_owner and not user.establishment == establishment:
            return {"error": "Usuário não é dono do estabelecimento e não pode atualizar os horários de funcionamento."}
        dict_day = json.loads(day)
        DAY_MAP = {
            'seg': 0,'ter': 1,'qua': 2,'qui': 3,'sex': 4,'sab': 5,'dom': 6,
        }
        day_number = DAY_MAP.get(dict_day['day'])
        if type == "update_day":
            day_user = establishment.operating_hours.get(day_of_week=day_number)
            day_user.is_closed = False if day_user.is_closed else True
            day_user.save()
            return {"success": f"Horário do dia {dict_day['day']} atualizado com sucesso."}