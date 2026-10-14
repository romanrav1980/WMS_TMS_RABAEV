from pathlib import Path
p=Path('api/wms_api_server/app/modules/transport/infrastructure/delivery_window_preview.py');s=p.read_text(encoding='utf-8')
needle='    result.update({"trip_id":trip,"source_hash":context["source_hash"],"consistent_snapshot":True})'
assert needle in s
replacement='''    profiles = {p["address"]: p for p in context["source"].get("store_window_profiles", [])}
    for stop in result.get("stops", []):
        profile = profiles.get(stop.get("address"))
        if profile is not None:
            stop["profile_version"] = profile.get("profile_version")
            stop["store_window_mode"] = profile.get("mode", "UNCONFIGURED")
            stop["store_time_zone"] = profile.get("time_zone")
            stop["configured_weekly_windows"] = profile.get("windows", [])
    result.update({"trip_id":trip,"source_hash":context["source_hash"],"consistent_snapshot":True})'''
p.write_text(s.replace(needle,replacement),encoding='utf-8')
