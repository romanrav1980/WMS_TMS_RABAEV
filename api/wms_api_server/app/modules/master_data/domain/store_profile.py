"""Профиль магазина: только явно заданные параметры, отсутствующих в RRL_ADDR и смежных политиках.

Незаданный параметр (None) ничего не означает и не влияет на планирование/допуск — интеграция с транспортом
и временем приёмки выполняется отдельно владельцем native-правил.
"""
from typing import Any

TEMP_CLASSES = ("AMBIENT", "CHILLED", "FROZEN")
UNLOAD_METHODS = ("PALLET", "ROLL_CAGE", "MANUAL")
FLAGS = ("backroom_flag", "unattended_drop_flag", "ramp_flag", "loader_required")
COUNTS = ("backroom_pallets", "backroom_rolls")
MILLIMETRES = ("ramp_height_mm",)
OUTER_LIMITS = ("max_vehicle_outer_height_mm", "max_vehicle_outer_length_mm")  # внешние габариты ТС, не размеры кузова
WINDOW_MODES = ("UNCONFIGURED", "WEEKLY")
FIELDS = FLAGS + COUNTS + MILLIMETRES + OUTER_LIMITS + ("receiving_window_mode", "storage_temp_class", "default_unload_method", "timezone_region", "access_note")
MAX_WINDOWS_PER_DAY = 8
MAX_WINDOWS_PER_WEEK = 56


class StoreProfileInvalid(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def normalize_windows(windows: list[dict[str, Any]], mode: str = "WEEKLY") -> list[dict[str, int]]:
    """Окна приёма WEEKLY: день недели ISO 1–7, полуоткрытые интервалы [from,to) в минутах, без пересечений.

    Отсутствующий день при WEEKLY означает «закрыто»; при UNCONFIGURED строк окон нет вовсе.
    Ночной интервал задаётся явно двумя днями. Превышение лимитов отклоняется, а не обрезается.
    """
    if mode == "UNCONFIGURED":
        if windows:
            raise StoreProfileInvalid("STORE_WINDOWS_UNCONFIGURED_ROWS", "Режим «не задано» не содержит интервалов")
        return []
    if len(windows) > MAX_WINDOWS_PER_WEEK:
        raise StoreProfileInvalid("STORE_WINDOW_LIMIT", f"Не более {MAX_WINDOWS_PER_WEEK} интервалов в неделю")
    rows: list[dict[str, int]] = []
    for window in windows:
        day, start, end = window.get("weekday"), window.get("from_minute"), window.get("to_minute")
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (day, start, end)):
            raise StoreProfileInvalid("STORE_WINDOW_INTEGER_REQUIRED", "День и минуты окна — целые числа")
        if not 1 <= day <= 7 or not 0 <= start < end <= 1440:
            raise StoreProfileInvalid("STORE_WINDOW_RANGE", "День 1–7, начало раньше конца, в пределах суток")
        rows.append({"weekday": day, "from_minute": start, "to_minute": end})
    rows.sort(key=lambda r: (r["weekday"], r["from_minute"]))
    for previous, current in zip(rows, rows[1:]):
        if previous["weekday"] == current["weekday"] and current["from_minute"] < previous["to_minute"]:
            raise StoreProfileInvalid("STORE_WINDOW_OVERLAP", "Окна приёма одного дня пересекаются")
    for day in range(1, 8):
        if sum(1 for r in rows if r["weekday"] == day) > MAX_WINDOWS_PER_DAY:
            raise StoreProfileInvalid("STORE_WINDOW_LIMIT", f"Не более {MAX_WINDOWS_PER_DAY} окон в день")
    return rows


def normalize_profile(values: dict[str, Any]) -> dict[str, Any]:
    profile = {name: values.get(name) for name in FIELDS}
    for name in FLAGS:
        if profile[name] is not None and not isinstance(profile[name], bool):
            raise StoreProfileInvalid("STORE_PROFILE_FLAG", f"{name}: да/нет или не задано")
    for name in COUNTS + MILLIMETRES + OUTER_LIMITS:
        value, low = profile[name], 1 if name in OUTER_LIMITS else 0
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not low <= value <= 100000):
            raise StoreProfileInvalid("STORE_PROFILE_NUMBER", f"{name}: целое {low}–100000 или не задано")
    mode = profile["receiving_window_mode"] or "UNCONFIGURED"
    if mode not in WINDOW_MODES:
        raise StoreProfileInvalid("STORE_WINDOW_MODE", "Режим окон: UNCONFIGURED или WEEKLY")
    profile["receiving_window_mode"] = mode
    if profile["storage_temp_class"] not in (None, *TEMP_CLASSES):
        raise StoreProfileInvalid("STORE_PROFILE_TEMP_CLASS", "Температурный класс подсобки не поддерживается")
    if profile["default_unload_method"] not in (None, *UNLOAD_METHODS):
        raise StoreProfileInvalid("STORE_PROFILE_UNLOAD_METHOD", "Способ разгрузки не поддерживается")
    if profile["backroom_flag"] is False and (profile["backroom_pallets"] or profile["backroom_rolls"]):
        raise StoreProfileInvalid("STORE_PROFILE_BACKROOM_CONFLICT", "Вместимость указана при отсутствии подсобки")
    if profile["ramp_flag"] is False and profile["ramp_height_mm"]:
        raise StoreProfileInvalid("STORE_PROFILE_RAMP_CONFLICT", "Высота рампы указана при отсутствии рампы")
    note = profile["access_note"]
    if note is not None and (not isinstance(note, str) or len(note) > 1000):
        raise StoreProfileInvalid("STORE_PROFILE_ACCESS_NOTE", "Примечание о подъезде — до 1000 символов")
    zone = profile["timezone_region"]
    if zone is not None and (not isinstance(zone, str) or not 3 <= len(zone) <= 64 or ("/" not in zone and zone != "UTC")):
        raise StoreProfileInvalid("STORE_PROFILE_TIMEZONE", "Часовой пояс в формате IANA, например Europe/Moscow")
    if mode == "WEEKLY" and zone is None:
        raise StoreProfileInvalid("STORE_PROFILE_TIMEZONE_REQUIRED", "Для недельного расписания нужен явный часовой пояс магазина")
    return profile
