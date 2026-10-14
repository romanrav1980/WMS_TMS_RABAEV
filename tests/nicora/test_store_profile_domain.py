import pytest
from app.modules.master_data.domain.store_profile import StoreProfileInvalid, normalize_profile, normalize_windows


def test_windows_sorted_and_non_overlapping():
    rows = normalize_windows([{"weekday": 2, "from_minute": 840, "to_minute": 1080}, {"weekday": 2, "from_minute": 480, "to_minute": 720}])
    assert [r["from_minute"] for r in rows] == [480, 840]


@pytest.mark.parametrize("windows,code", [
    ([{"weekday": 1, "from_minute": 480, "to_minute": 720}, {"weekday": 1, "from_minute": 700, "to_minute": 800}], "STORE_WINDOW_OVERLAP"),
    ([{"weekday": 8, "from_minute": 0, "to_minute": 60}], "STORE_WINDOW_RANGE"),
    ([{"weekday": 1, "from_minute": 600, "to_minute": 600}], "STORE_WINDOW_RANGE"),
    ([{"weekday": 1, "from_minute": True, "to_minute": 60}], "STORE_WINDOW_INTEGER_REQUIRED"),
])
def test_invalid_windows(windows, code):
    with pytest.raises(StoreProfileInvalid) as error:
        normalize_windows(windows)
    assert error.value.code == code


def test_unset_parameters_stay_unset():
    profile = normalize_profile({})
    assert profile.pop("receiving_window_mode") == "UNCONFIGURED"
    assert all(value is None for value in profile.values())


def test_unconfigured_has_no_rows_and_weekly_needs_timezone():
    with pytest.raises(StoreProfileInvalid) as error:
        normalize_windows([{"weekday": 1, "from_minute": 0, "to_minute": 60}], "UNCONFIGURED")
    assert error.value.code == "STORE_WINDOWS_UNCONFIGURED_ROWS"
    with pytest.raises(StoreProfileInvalid) as error:
        normalize_profile({"receiving_window_mode": "WEEKLY"})
    assert error.value.code == "STORE_PROFILE_TIMEZONE_REQUIRED"
    assert normalize_windows([], "WEEKLY") == []  # неделя целиком закрыта — допустимо и отличается от «не задано»


def test_day_and_week_limits():
    day = [{"weekday": 1, "from_minute": i * 60, "to_minute": i * 60 + 30} for i in range(9)]
    with pytest.raises(StoreProfileInvalid):
        normalize_windows(day)
    week = [{"weekday": d, "from_minute": i * 60, "to_minute": i * 60 + 30} for d in range(1, 8) for i in range(9)][:57]
    with pytest.raises(StoreProfileInvalid):
        normalize_windows(week)


def test_outer_limits_positive():
    with pytest.raises(StoreProfileInvalid):
        normalize_profile({"max_vehicle_outer_height_mm": 0})


@pytest.mark.parametrize("values,code", [
    ({"backroom_flag": False, "backroom_pallets": 4}, "STORE_PROFILE_BACKROOM_CONFLICT"),
    ({"ramp_flag": False, "ramp_height_mm": 1200}, "STORE_PROFILE_RAMP_CONFLICT"),
    ({"storage_temp_class": "HOT"}, "STORE_PROFILE_TEMP_CLASS"),
    ({"timezone_region": "Moscow"}, "STORE_PROFILE_TIMEZONE"),
    ({"backroom_pallets": -1}, "STORE_PROFILE_NUMBER"),
])
def test_invalid_profile(values, code):
    with pytest.raises(StoreProfileInvalid) as error:
        normalize_profile(values)
    assert error.value.code == code
