import json

class OperationDayService:
    @staticmethod
    def update_operating_hours(day):
        dict_day = json.loads(day)
        print(day)
        print(type(dict_day))
        print(dict_day)
        # Você pode acessar o modelo de horários de funcionamento do estabelecimento e atualizar o status do dia
        pass