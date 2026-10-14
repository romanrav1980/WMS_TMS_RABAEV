# C-0029 live (разрешено C-0035): собственный dev-адрес Own264, существующий PUT/GET профиля. Чужие адреса не трогаются,
# история не удаляется; в конце исходные параметры (UNCONFIGURED, всё не задано) возвращаются новой версией.
import base64, json, re, sys, time, urllib.request, urllib.error, uuid
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = ["C:/projects/TMS/scripts", "C:/projects/TMS/api/wms_api_server"]
pw = re.search(r"PASS=(\S+?)[`,)\s]", open("C:/projects/TMS/AGENTS.md", encoding="utf-8").read()).group(1)
H = {"Authorization": "Basic " + base64.b64encode(f"admin:{pw}".encode()).decode()}
BASE = "http://127.0.0.1:8088/api/master-data/stores/profile"
ADDR = "Own264 synthetic registered store 288ec8b68a"
NULLS = {k: None for k in ("timezone_region", "backroom_flag", "backroom_pallets", "backroom_rolls", "unattended_drop_flag", "storage_temp_class", "ramp_flag",
                           "ramp_height_mm", "max_vehicle_outer_height_mm", "max_vehicle_outer_length_mm", "default_unload_method", "loader_required", "access_note")}
out = []


def call(method, body=None):
    t = time.perf_counter()
    req = urllib.request.Request(BASE + ("?addr=" + quote(ADDR) if method == "GET" else ""), data=json.dumps(body).encode() if body else None,
                                 headers={**H, "Content-Type": "application/json"}, method=method)
    try:
        status, data = 200, json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        status, data = e.code, json.loads(e.read() or b"{}")
    return status, data, round((time.perf_counter() - t) * 1000)


def step(name, method, body=None, keep=None):
    status, data, ms = call(method, body)
    summary = {k: data.get(k) for k in ("version", "configured", "operation_id")} if status == 200 else data.get("detail")
    if status == 200 and "windows" in data:
        summary["windows"] = len(data["windows"]); summary["mode"] = (data.get("profile") or {}).get("receiving_window_mode"); summary["tz"] = (data.get("profile") or {}).get("timezone_region")
    out.append({"step": name, "http": status, "ms": ms, "result": summary}); print(json.dumps(out[-1], ensure_ascii=False))
    return status, data


def body(version, reason, **values):
    return {"operation_id": "STORE.PROFILE:C0029:" + uuid.uuid4().hex, "store_addr": ADDR, "expected_version": version, "reason": reason, **NULLS, **values}


st, cur = step("read_initial", "GET")
v = cur["version"]
weekly = body(v, "DEV.C0029 live weekly schedule", receiving_window_mode="WEEKLY", timezone_region="Europe/Moscow", backroom_flag=True, backroom_pallets=6,
              storage_temp_class="AMBIENT", ramp_flag=False, max_vehicle_outer_height_mm=4000, max_vehicle_outer_length_mm=12000, default_unload_method="PALLET",
              loader_required=False, windows=[{"weekday": d, "from_minute": f, "to_minute": t} for d in range(1, 6) for f, t in ((480, 780), (840, 1200))])
step("put_weekly", "PUT", weekly)
step("read_after_weekly", "GET")
step("replay_same_operation", "PUT", weekly)
step("same_operation_other_body", "PUT", {**weekly, "backroom_pallets": 7})
step("stale_version_new_operation", "PUT", body(v, "DEV.C0029 stale version", receiving_window_mode="UNCONFIGURED"))
full = body(v + 1, "DEV.C0029 full week 56 windows", receiving_window_mode="WEEKLY", timezone_region="Europe/Moscow",
            windows=[{"weekday": d, "from_minute": i * 180, "to_minute": i * 180 + 120} for d in range(1, 8) for i in range(8)])
step("put_56_windows", "PUT", full)
st, read56 = step("read_56_windows", "GET")
over = body(v + 2, "DEV.C0029 57 windows must fail", receiving_window_mode="WEEKLY", timezone_region="Europe/Moscow",
            windows=full["windows"] + [{"weekday": 1, "from_minute": 1430, "to_minute": 1440}])
step("put_57_windows_rejected", "PUT", over)
step("bad_timezone_rejected", "PUT", body(v + 2, "DEV.C0029 bad timezone", receiving_window_mode="WEEKLY", timezone_region="Mars/Olympus", windows=[]))
step("restore_initial", "PUT", body(v + 2, "DEV.C0029 restore initial parameters", receiving_window_mode="UNCONFIGURED"))
step("read_final", "GET")
json.dump(out, open("C:/projects/TMS/reports/retailcase/2026-10-13/claude/C0029/c0029_live_profile.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
