"""Проверка параметров GET перед передачей в SQL."""

from datetime import date


def integer(request, name, default=0, minimum=0, maximum=1000000):
    raw = request.GET.get(name, str(default))
    try:
        value = int(raw)
    except (ValueError, TypeError):
        raise ValueError("Параметр должен быть целым числом.") from None
    if not minimum <= value <= maximum:
        raise ValueError("Число вне допустимого диапазона.")
    return value


def selected_date(request):
    value = request.GET.get("date", "").strip()
    if value:
        try:
            if date.fromisoformat(value).isoformat() != value:
                raise ValueError
        except ValueError:
            raise ValueError("Дата должна иметь формат ГГГГ-ММ-ДД.")
    return value
