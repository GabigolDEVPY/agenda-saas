from datetime import datetime
import json
from .messages import ERRORS, SUCCESS

class OperationDayService:
    @staticmethod
    def update_operating_hours(clean_data, user):
        establishment = user.owned_establishment

        if not establishment:
            return {"status": "error", "message": ERRORS["ESTABLISHMENT_NOT_FOUND"]}

        DAY_MAP = {
            'seg': 0,'ter': 1,'qua': 2,'qui': 3,'sex': 4,'sab': 5,'dom': 6,
        }

        day_number = DAY_MAP.get(clean_data["day"])

        day_user = establishment.operating_hours.filter(day_of_week=day_number).first()

        if not day_user:
            return {"status": "error", "message": ERRORS["DAY_NOT_FOUND"]}

        if clean_data["type"] == "update_day":
            day_user.is_closed = not day_user.is_closed

        elif clean_data["type"] == "update_time":
            if day_user.is_closed:
                return {"status": "error", "message": ERRORS["DAY_CLOSED"]}

            day_user.open_time = clean_data["abertura"]
            day_user.close_time = clean_data["fechamento"]

        else:
            return {"status": "error", "message": ERRORS["TYPE_INVALID"]}

        day_user.save()

        return {"status": "success", "message": SUCCESS["DAY_UPDATED"]}