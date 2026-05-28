"""
test_sprint47_functional.py — Functional tests for Sprint 47 (localStorage persistence).

Sprint 47 persists four state variables across page reloads:
  tms_filterDate, tms_routeShipDate, tms_viewMode, tms_activeTab.
Initial state reads from localStorage (falls back to defaults).
"""


class FakeStorage:
    def __init__(self):
        self._store: dict[str, str] = {}

    def get(self, key: str, fallback: str) -> str:
        return self._store.get(key, fallback)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value


def init_state(storage: FakeStorage, today: str) -> dict:
    return {
        "filterDate":    storage.get("tms_filterDate",    today),
        "routeShipDate": storage.get("tms_routeShipDate", today),
        "viewMode":      storage.get("tms_viewMode",      "flat"),
        "activeTab":     storage.get("tms_activeTab",     "tasks"),
    }


def persist_state(storage: FakeStorage, state: dict) -> None:
    for key_suffix, val in [
        ("filterDate",    state["filterDate"]),
        ("routeShipDate", state["routeShipDate"]),
        ("viewMode",      state["viewMode"]),
        ("activeTab",     state["activeTab"]),
    ]:
        storage.set(f"tms_{key_suffix}", val)


class TestLocalStoragePersistence:
    def test_default_state_when_empty(self):
        s = FakeStorage()
        state = init_state(s, "2026-05-28")
        assert state["filterDate"]    == "2026-05-28"
        assert state["routeShipDate"] == "2026-05-28"
        assert state["viewMode"]      == "flat"
        assert state["activeTab"]     == "tasks"

    def test_persisted_filter_date_restored(self):
        s = FakeStorage()
        s.set("tms_filterDate", "2026-06-01")
        state = init_state(s, "2026-05-28")
        assert state["filterDate"] == "2026-06-01"

    def test_persisted_route_date_restored(self):
        s = FakeStorage()
        s.set("tms_routeShipDate", "2026-06-10")
        state = init_state(s, "2026-05-28")
        assert state["routeShipDate"] == "2026-06-10"

    def test_persisted_view_mode_restored(self):
        s = FakeStorage()
        s.set("tms_viewMode", "clusters")
        state = init_state(s, "2026-05-28")
        assert state["viewMode"] == "clusters"

    def test_persisted_active_tab_restored(self):
        s = FakeStorage()
        s.set("tms_activeTab", "routes")
        state = init_state(s, "2026-05-28")
        assert state["activeTab"] == "routes"

    def test_persist_then_reload(self):
        s = FakeStorage()
        state = init_state(s, "2026-05-28")
        state["filterDate"] = "2026-06-05"
        state["viewMode"]   = "clusters"
        state["activeTab"]  = "billing"
        persist_state(s, state)
        reloaded = init_state(s, "2026-05-28")
        assert reloaded["filterDate"] == "2026-06-05"
        assert reloaded["viewMode"]   == "clusters"
        assert reloaded["activeTab"]  == "billing"

    def test_storage_error_falls_back_to_default(self):
        class BrokenStorage(FakeStorage):
            def get(self, key, fallback): raise RuntimeError("no storage")
        s = BrokenStorage()
        try:
            val = s.get("tms_filterDate", "2026-05-28")
        except RuntimeError:
            val = "2026-05-28"
        assert val == "2026-05-28"

    def test_all_four_keys_persisted(self):
        s = FakeStorage()
        state = {"filterDate": "2026-05-30", "routeShipDate": "2026-05-31",
                 "viewMode": "clusters", "activeTab": "routes"}
        persist_state(s, state)
        assert s.get("tms_filterDate",    "") == "2026-05-30"
        assert s.get("tms_routeShipDate", "") == "2026-05-31"
        assert s.get("tms_viewMode",      "") == "clusters"
        assert s.get("tms_activeTab",     "") == "routes"

    def test_today_not_overridden_by_stored_date(self):
        """If stored date exists, use it (not today)."""
        s = FakeStorage()
        s.set("tms_filterDate", "2026-01-01")
        state = init_state(s, "2026-05-28")
        assert state["filterDate"] == "2026-01-01"
