from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py");s=p.read_text(encoding="utf-8")
start=s.index('        header = trip_scope(cur, trip, actor)')
old=s[start:]
assert old.endswith('\n')
body='\n'.join(line[4:]if line.startswith('    ')else line for line in old.splitlines())+'\n'
s=s[:start]+'        return read_trip_time(cur,trip,zone,actor)\n\n\ndef read_trip_time(cur: Any,trip: int,zone: str,actor: str) -> dict[str,Any]:\n'+body
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/delivery_window_preview.py");s=p.read_text(encoding="utf-8")
start=s.index('            cur.callproc("RRL_TT_ROUTE_API.context"')
end=s.index('    except oracledb.DatabaseError')
body=s[start:end]
body='\n'.join(line[8:]if line.startswith('        ')else line for line in body.splitlines())+'\n'
s=s[:s.index('            cur.execute("set transaction read only")')]+'''            cur.execute("set transaction read only")
            return read_delivery_windows(cur,trip,depot,max_age,zone,actor)
    except oracledb.DatabaseError as exc:raise trip_error(exc)from exc

def read_delivery_windows(cur: Any,trip: int,depot: str,max_age: int,zone: str,actor: str) -> dict:
    out=cur.var(oracledb.DB_TYPE_CLOB)
'''+body
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8")
s=s.replace('from .loading_status import read_loading_status','from .loading_status import read_loading_status\nfrom .time_preflight import read_trip_time\nfrom .delivery_window_preview import read_delivery_windows')
needle='            placed=0'
assert needle in s
s=s.replace(needle,'''            if time["approval_status"]=="APPROVED":
                zone=time["last_approval"]["time_zone"]
                temporal=read_trip_time(cur,trip,zone,actor)
                windows=read_delivery_windows(cur,trip,"",24,zone,actor)
                blockers.extend({"code":"COORDINATION_RESOURCE_CONFLICT","trip_id":x["trip_id"]}for x in temporal["conflicts"])
                blockers.extend({"code":x["code"]}for x in temporal["issues"])
                blockers.extend({"code":x["code"]}for x in temporal["driver_rest"]["violations"])
                blockers.extend({"code":x["code"]}for x in temporal["driver_rest"]["unknown_intervals"])
                blockers.extend({"code":x["code"],"address":x.get("address")}for x in windows["issues"])
                if temporal["driver_days"]["status"]!="NO_RECORDED_DAY_VIOLATION":
                    blockers.append({"code":"COORDINATION_DRIVER_DAY_NOT_VERIFIED"})
            else:
                temporal={"status":"CURRENT_APPROVED_REGION_REQUIRED"}
                windows={"status":"CURRENT_APPROVED_REGION_REQUIRED","operational_admission":False}
            placed=0''',1)
s=s.replace('"time":time,"loading":load,','"time":time,"temporal":temporal,"delivery_windows":windows,"loading":load,')
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
