DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

# Ordem comercial: Seg=0, Ter=1, ..., Sáb=5, Dom=6
COMMERCIAL_ORDER = [1, 2, 3, 4, 5, 6, 0]

def group_operating_hours(hours_qs):
    open_days = list(hours_qs.filter(is_closed=False).order_by('day_of_week'))
    
    if not open_days:
        return []

    # Reordena para Seg→Dom
    open_days.sort(key=lambda h: COMMERCIAL_ORDER.index(h.day_of_week))

    groups = []
    start = open_days[0]
    end = open_days[0]

    for current in open_days[1:]:
        same_hours = (
            current.open_time == end.open_time and
            current.close_time == end.close_time
        )
        # Consecutivo na ordem comercial
        consecutive = (
            COMMERCIAL_ORDER.index(current.day_of_week) ==
            COMMERCIAL_ORDER.index(end.day_of_week) + 1
        )

        if same_hours and consecutive:
            end = current
        else:
            groups.append(_format_group(start, end))
            start = current
            end = current

    groups.append(_format_group(start, end))
    return groups


def _format_group(start, end):
    open_t = start.open_time.strftime('%H:%M')
    close_t = start.close_time.strftime('%H:%M')

    if start.day_of_week == end.day_of_week:
        day_label = DAYS[start.day_of_week]
    else:
        day_label = f'{DAYS[start.day_of_week]}–{DAYS[end.day_of_week]}'

    return f'{day_label}: {open_t} às {close_t}'