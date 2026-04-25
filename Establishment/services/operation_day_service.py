import json

class OperationDayService:
    @staticmethod
    def update_operating_hours(data, user, establishment):
        if not user.is_owner and not user.establishment == establishment:
            return {"status": "error", "message": "Usuário não é dono do estabelecimento e não pode atualizar os horários de funcionamento."}
        dict_data = json.loads(data)
        type = dict_data.get('type')
        DAY_MAP = {
            'seg': 0,'ter': 1,'qua': 2,'qui': 3,'sex': 4,'sab': 5,'dom': 6,
        }
        day_number = DAY_MAP.get(dict_data['day'])
        day_user = establishment.operating_hours.get(day_of_week=day_number)

        if type == "update_day":

            day_user.is_closed = False if day_user.is_closed else True
            day_user.save()
        
        elif type == "update_time":

            abertura = dict_data.get('abertura')
            fechamento = dict_data.get('fechamento')
            if not abertura or not fechamento:
                return {"status": "error", "message": "Horário de abertura e fechamento são obrigatórios para atualizar os horários."}
            
            day_user.open_time = abertura
            day_user.close_time = fechamento
            day_user.save()