"""C-0167 offline checks: vehicle change reuses the existing native transitions (edit before loading, unload first after loading, frozen
after departure, only the current vehicle confirms loading) — LIVE READ ONLY evidence — and the dispatcher block explains them."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/tradecase/2026-10-23/claude/C0167"
UI = ROOT / "admin/wms_admin_frontend/src"


def test_native_transitions_exist_live():
    e = json.loads((REPORT / "native-evidence.json").read_text(encoding="utf-8"))
    assert e["all_true"] and e["trigger"]["status"] == "ENABLED"
    edit = e["objects"]["RRL_TRANSPORT_EDIT_API:PACKAGE BODY"]["checks"]
    assert edit["loaded_or_departed_refused"] and edit["capacity_check_of_new_vehicle"] and edit["assignments_untouched"]
    assert e["objects"]["RRL_STOCK_HU_LOAD_CORE:PACKAGE BODY"]["checks"]["scan_must_be_current_vehicle"]
    assert e["objects"]["RRL_STOCK_UNLOAD_CMD:PACKAGE BODY"]["checks"]["unload_scan_vehicle_dock_cell_reason"]
    assert e["objects"]["RRL_TRADE_TRANSPORT_CORE:PACKAGE BODY"]["checks"]["departure_needs_document_of_current_manifest"]


def test_dispatcher_block_reads_only_and_explains_each_state():
    s = (UI / "features/transport/VehicleChange.tsx").read_text(encoding="utf-8")
    assert "/api/transport/loading/${taskId}/status" in s and "method:" not in s  # a read of the existing status, no command
    for words in ("смена машины недоступна", "Сначала выгрузите погруженные места", "машину можно сменить", "скан новой машины",
                  "transport-loading.html?trip_id="):
        assert words in s
    assert "setData(null);  // 401/403/404" in s and "controller.abort()" in s and "value.trip.id === taskId" in s
    for code in ("TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT", "TRANSPORT_PLAN_FROZEN", "TRANSPORT_VEHICLE_CHANGED_RETRY"):
        assert code in s
    for el in s.split("<button")[1:] + s.split("<a ")[1:]:
        head = el.split(">")[0]
        assert "title=" in head and "data-help-id=" in head


def test_dispatch_page_wiring_is_narrow():
    p = (UI / "components/TransportDispatchPage.tsx").read_text(encoding="utf-8")
    assert "<VehicleChange key={selectedTask.ID} taskId={selectedTask.ID} editing={editMode} onTask={refreshTask} />" in p
    assert "await saveTripEdit(selectedTask, editRef.current);" in p and "setError(vehicleChangeError(String(e)))" in p
    assert 'typeof b?.detail === "object" && b.detail ? JSON.stringify(b.detail)' in p  # no more "409: [object Object]"
    help_page = (ROOT / "admin/wms_admin_frontend/public/help/transport-vehicle-change.html").read_text(encoding="utf-8")
    assert "Рейс выехал" in help_page and "Открыть выгрузку рейса" in help_page and "одной кнопкой" in help_page


def test_unknown_outcome_intent_rules():
    s = (UI / "features/transport/vehicleEditIntent.ts").read_text(encoding="utf-8")
    assert "localStorage.setItem(key, raw); if (localStorage.getItem(key) === raw)" in s  # stored and verified before sending
    assert "if (readIntent(trip.ID)) throw" in s  # no new edit replaces an unresolved original
    assert s.index("if (!intent.unknown) { settle(intent.trip_id, raw); throw e; }") < s.index("markUnknown(intent, raw);")
    assert "operation_id" not in s  # a metadata SET: no invented operation id or exactly-once claim
    v = (UI / "features/transport/VehicleChange.tsx").read_text(encoding="utf-8")
    assert "disabled={busy || !readOk}" in v and v.count("disabled={busy || !readOk}") == 2  # retry/discard only after a successful read
    css = (UI / "features/transport/dispatchNarrow.css").read_text(encoding="utf-8")
    assert "@media (max-width: 760px)" in css and "body:has(.dispatch-shell) { min-width: 0; }" in css
