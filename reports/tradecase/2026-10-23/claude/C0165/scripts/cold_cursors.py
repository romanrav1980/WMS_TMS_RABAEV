"""C-0165 READ ONLY: cursors (re)loaded into the shared pool by the cold call at the given time (V$SQL is readable; V$SQLSTATS,
V$MYSTAT and V$DB_OBJECT_CACHE are not). Grouped by the PL/SQL unit that owns them (PROGRAM_ID). Usage: cold_cursors.py <from> <to>."""
import json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

lo, hi = sys.argv[1], sys.argv[2]
with OracleGateway().transaction("C-0165 cold cursor read READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("""select nvl(o.object_name,'(top level)') unit,s.program_line#,s.executions,round(s.elapsed_time/1000,1) total_ms,
        round(s.elapsed_time/greatest(s.executions,1)/1000,1) per_exec_ms,s.loads,substr(s.sql_text,1,90) text
        from v$sql s left join user_objects o on o.object_id=s.program_id
        where s.first_load_time between :lo and :hi and s.parsing_schema_name=user order by s.elapsed_time desc""", lo=lo, hi=hi)
    rows = [dict(zip([d[0].lower() for d in cur.description], r)) for r in cur.fetchall()]
    cur.execute("rollback")
units = {}
for r in rows:
    u = units.setdefault(r["unit"], {"cursors": 0, "total_ms": 0.0})
    u["cursors"] += 1; u["total_ms"] = round(u["total_ms"] + r["total_ms"], 1)
res = {"window": [lo, hi], "cursors": len(rows), "total_ms": round(sum(r["total_ms"] for r in rows), 1),
       "by_unit": dict(sorted(units.items(), key=lambda x: -x[1]["total_ms"])), "top": rows[:25]}
pathlib.Path(__file__).resolve().parents[1].joinpath(f"cold-cursors-{lo[-8:].replace(':', '')}.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: res[k] for k in ("cursors", "total_ms")}), json.dumps(list(res["by_unit"].items())[:12], ensure_ascii=False))
for r in rows[:12]: print(r["per_exec_ms"], r["executions"], r["unit"], r["program_line#"], r["text"][:70])
