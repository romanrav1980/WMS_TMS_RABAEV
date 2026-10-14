# C-0010: проверка результата цикла и SQL-решение по реестру. Только чтение.
import json, sys, time
from hashlib import sha256
from pathlib import Path

ROOT = Path("C:/projects/TMS")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server"), str(ROOT / "api/wms_api_server/app/modules/finance/infrastructure")]
import oracledb
from stock_posting_environment import load_local_oracle_environment

load_local_oracle_environment()
from app.config import get_settings
from expense_register_read import LATEST_SQL, EXACT_SQL

s = get_settings()
cycle = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["after"]
out = {}
with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
    q = c.cursor()
    events = [("EXTRA_EXPENSE_RECOGNIZED", d["operation_id"]) for d in cycle["decisions"] if d["phase"] == "FINANCE"]
    events += [("EXTRA_EXPENSE_ALLOCATED", a["operation_id"]) for a in cycle["allocations"]]
    out["outbox"] = []
    for kind, op in events:
        event = "FIN:" + sha256((kind + ":" + op).encode()).hexdigest()
        q.execute("select count(*) from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:e", e=event)
        out["outbox"].append({"event_type": kind, "operation_id": op, "rows": q.fetchone()[0]})
    q.execute("select count(*) from RRL_LOGISTICS_EXP_ALLOCATION a join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=a.EXPENSE_OPERATION_ID where e.DOCUMENT_REFERENCE like 'DEV.C0010%'")
    out["allocations_total"] = q.fetchone()[0]
    q.execute("select count(*) from RRL_LOGISTICS_EXPENSE where DOCUMENT_REFERENCE like 'DEV.C0010%'")
    out["expenses_total"] = q.fetchone()[0]
    q.execute("""select l.LOAD_OPERATION_ID,l.ARTICLE,to_char(l.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY,to_char(l.AMOUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AMOUNT
        from RRL_LOGISTICS_EXP_ALLOC_LINE l join RRL_LOGISTICS_EXP_ALLOCATION a on a.OPERATION_ID=l.OPERATION_ID join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=a.EXPENSE_OPERATION_ID
        where e.DOCUMENT_REFERENCE like 'DEV.C0010%' order by a.OPERATION_ID,l.LOAD_OPERATION_ID""")
    out["allocation_lines"] = [list(map(str, r)) for r in q.fetchall()]
    timing = {}
    for name, sql, params in [("latest_100_ware_9807", LATEST_SQL, {"ware": 9807}), ("latest_100_ware_2378876", LATEST_SQL, {"ware": 2378876}),
                              ("exact_ware_9807", EXACT_SQL, {"ware": 9807, "op": cycle["expenses"][0]["operation_id"]})]:
        runs = []
        for _ in range(5):
            t = time.perf_counter(); q.execute(sql, params); n = len(q.fetchall()); runs.append(round((time.perf_counter() - t) * 1000, 1))
        timing[name] = {"rows": n, "ms": runs}
    out["sql_timing"] = timing
    q.execute("select index_name,listagg(column_name,',') within group(order by column_position) from user_ind_columns where table_name='RRL_LOGISTICS_EXPENSE' group by index_name")
    out["expense_indexes"] = q.fetchall()
print(json.dumps(out, ensure_ascii=False, indent=1))
Path(sys.argv[1]).with_name("c0010_verify.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
