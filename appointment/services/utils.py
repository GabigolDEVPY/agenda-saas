def to_min(hhmm: str) -> int:
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def error(uid: str, horario: str, title: str, message: str) -> dict:
    return {
        "status":  "error",
        "horario": horario,
        "title":   title,
        "message": message,
        "uid":     uid,
    }


def operating_hours_for_date(cfg: dict, date):
    horarios = cfg.get("horarios_funcionamento") or {}
    js_day = (date.weekday() + 1) % 7
    day_cfg = horarios.get(str(js_day))

    if day_cfg:
        return day_cfg

    return {
        "aberto": True,
        "inicio": cfg.get("hora_inicio", "09:00"),
        "fim": cfg.get("hora_fim", "18:00"),
    }
