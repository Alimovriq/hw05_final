import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    local_time = dt.datetime.today()
    return {
        "year": local_time.year,
    }
