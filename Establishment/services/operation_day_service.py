from datetime import datetime
import json
from .messages import ERRORS, SUCCESS

class OperationDayService:
    @staticmethod
    def update_operating_hours(data, user):
        establishment = user.owned_establishment
        if not establishment:
            return {"status": "error", "message": ERRORS["ESTABLISHMENT_NOT_FOUND"]}
        
        dict_data = data if isinstance(data, dict) else json.loads(data) 
        type = dict_data.get('type')
        DAY_MAP = {
            'seg': 0,'ter': 1,'qua': 2,'qui': 3,'sex': 4,'sab': 5,'dom': 6,
        }
        day_key = dict_data.get('day')
        if not day_key:
            return {"status": "error", "message": ERRORS["DAY_REQUIRED"]}
        day_number = DAY_MAP.get(day_key) 

        if day_number is None:
            return {"status": "error", "message": ERRORS["DAY_INVALID"]}
        
        day_user = establishment.operating_hours.filter(day_of_week=day_number).first()
        if not day_user:
            return {"status": "error", "message": ERRORS["DAY_NOT_FOUND"]}
        
        if type == "update_day":
            day_user.is_closed = not day_user.is_closed
            day_user.save()
            return {"status": "success", "message": SUCCESS["DAY_UPDATED"]}
        
        elif type == "update_time":
            if day_user.is_closed:
                return {"status": "error", "message": ERRORS["DAY_CLOSED"]}

            
        
            try:
                abertura = datetime.strptime(dict_data.get('abertura'), "%H:%M").time()
                fechamento = datetime.strptime(dict_data.get('fechamento'), "%H:%M").time()
                if not abertura or not fechamento:
                    return {"status": "error", "message": ERRORS["TIME_REQUIRED"]}
                
                if abertura >= fechamento:
                    return {"status": "error", "message": ERRORS["TIME_INVALID_RANGE"]}
                day_user.open_time = abertura
                day_user.close_time = fechamento
                
            except ValueError:
                return {"status": "error", "message": ERRORS["TIME_INVALID_FORMAT"]}
    
            day_user.save()
            return {"status": "success", "message": SUCCESS["TIME_UPDATED"]}
        else:
            return {"status": "error", "message": ERRORS["TYPE_INVALID"]}