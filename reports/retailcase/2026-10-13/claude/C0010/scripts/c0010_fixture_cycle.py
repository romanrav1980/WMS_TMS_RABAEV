# C-0010: собственный dev fixture и реальный цикл допрасхода через UI.
# Пользователи C0010_LOGIST / C0010_FINANCE (WARE_ID=9807, не GLOBAL_ADMIN). Пароли случайные, живут только
# в памяти этого процесса и в Oracle; передаются UI-сценарию через окружение дочернего процесса и не печатаются.
import json, os, secrets, subprocess, sys
from pathlib import Path

ROOT = Path("C:/projects/TMS")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
import oracledb, httpx
from stock_posting_environment import load_local_oracle_environment

load_local_oracle_environment()
from app.config import get_settings

s = get_settings()
OUT = Path(sys.argv[1])
USERS = {"C0010_LOGIST": ["wms_admin_login", "transport_dispatch_view", "edit_bill_tt", "calc_tt_price"],
         "C0010_FINANCE": ["wms_admin_login", "transport_dispatch_view", "create_tt_price"]}
WARE, TRIP = 9807, 33571


def ensure_users(c):
    q = c.cursor(); fresh = {}
    for user in USERS:
        q.execute("select count(*) from USER_GROUP where ID=:id", id=user)
        if q.fetchone()[0] == 0:
            q.execute("insert into USER_GROUP(ID,NAME)values(:id,'Own C0010 dev expense participant')", id=user)
        secret = secrets.token_urlsafe(18); fresh[user] = secret
        q.execute("select count(*) from RUSERS where ID=:id", id=user)
        if q.fetchone()[0] == 0:
            q.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED)values(:id,'Own C0010 dev expense participant',:secret,:grp,:ware,0)", id=user, secret=secret, grp=user, ware=WARE)
        else:
            q.execute("update RUSERS set PASS=:secret,WARE_ID=:ware,DELETED=0 where ID=:id and USER_GROUP=:id", id=user, secret=secret, ware=WARE)
    c.commit()
    q.execute("select PASS from RUSERS where ID='admin'"); admin = q.fetchone()[0]
    return fresh, admin


def grant(admin):
    granted = {}
    with httpx.Client(base_url="http://127.0.0.1:8088", auth=("admin", admin), timeout=30) as client:
        for group, rights in USERS.items():
            have = {r.get("right_name") or r.get("right1") for r in client.get(f"/api/admin/rights/groups/{group}/rights").json()}
            for right in rights:
                if right not in have:
                    client.post(f"/api/admin/rights/groups/{group}/rights", json={"right_name": right, "description": "Own C0010 dev expense fixture"}).raise_for_status()
            granted[group] = sorted({r.get("right_name") or r.get("right1") for r in client.get(f"/api/admin/rights/groups/{group}/rights").json()})
    return granted


def snapshot(c, tag):
    q = c.cursor()
    def rows(sql, **p):
        q.execute(sql, p); cols = [d[0].lower() for d in q.description]
        return [{k: (str(v) if v is not None else None) for k, v in zip(cols, r)} for r in q.fetchall()]
    exp = rows("select OPERATION_ID,ARTICLE_CODE,to_char(AMOUNT*ADJUSTMENT_SIGN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') AMOUNT,CURRENCY,DOCUMENT_REFERENCE,CORRECTION_OF_OP,ACTOR from RRL_LOGISTICS_EXPENSE where OBJECT_KIND='TRIP' and OBJECT_ID=:t and DOCUMENT_REFERENCE like 'DEV.C0010%' order by CREATED_AT", t=TRIP)
    ids = [e["operation_id"] for e in exp]
    dec = rows("select d.EXPENSE_OPERATION_ID,d.OPERATION_ID,d.PHASE,d.OUTCOME,d.DISTRIBUTION_BASIS,d.DECISION_REFERENCE,d.ACTOR from RRL_LOGISTICS_EXP_DECISION d join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=d.EXPENSE_OPERATION_ID where e.OBJECT_ID=:t and e.DOCUMENT_REFERENCE like 'DEV.C0010%' order by d.CREATED_AT", t=TRIP)
    alloc = rows("""select a.EXPENSE_OPERATION_ID,a.OPERATION_ID,a.DISTRIBUTION_BASIS,to_char(a.AMOUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HEADER_AMOUNT,
        (select count(*) from RRL_LOGISTICS_EXP_ALLOC_LINE l where l.OPERATION_ID=a.OPERATION_ID) LINES,
        (select to_char(sum(l.AMOUNT),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_LOGISTICS_EXP_ALLOC_LINE l where l.OPERATION_ID=a.OPERATION_ID) LINES_SUM
        from RRL_LOGISTICS_EXP_ALLOCATION a join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=a.EXPENSE_OPERATION_ID where e.OBJECT_ID=:t and e.DOCUMENT_REFERENCE like 'DEV.C0010%'""", t=TRIP)
    op_ids = ids + [d["operation_id"] for d in dec] + [a["operation_id"] for a in alloc]
    outbox = []
    stock = 0
    for op in op_ids:
        outbox += rows("select EVENT_ID,EVENT_TYPE from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID like :p", p="%" + op + "%")
        q.execute("select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:op", op=op); stock += q.fetchone()[0]
    loads = rows("select LOAD_OPERATION_ID,STATUS from RRL_TT_HU_LOAD_FACT where TT_ID=:t order by LOAD_OPERATION_ID", t=TRIP)
    return {"tag": tag, "expenses": exp, "decisions": dec, "allocations": alloc, "outbox": outbox, "stock_operations_with_expense_ids": stock, "trip_loads": loads}


def main():
    with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
        fresh, admin = ensure_users(c)
        before = snapshot(c, "before")
    granted = grant(admin)
    env = dict(os.environ, C0010_A_USER="C0010_LOGIST", C0010_A_PW=fresh["C0010_LOGIST"], C0010_B_USER="C0010_FINANCE", C0010_B_PW=fresh["C0010_FINANCE"])
    run = subprocess.run(["node", str(Path(__file__).with_name("c0010_ui_cycle.cjs")), str(OUT)], env=env, capture_output=True, text=True, encoding="utf-8")
    for secret in fresh.values():
        assert secret not in run.stdout and secret not in run.stderr
    with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
        after = snapshot(c, "after")
    result = {"granted": granted, "before": before, "after": after, "ui_exit": run.returncode, "ui_stdout_tail": run.stdout[-6000:], "ui_stderr_tail": run.stderr[-3000:]}
    (OUT.parent / "c0010_cycle_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"ui_exit": run.returncode, "granted": granted, "after": after}, ensure_ascii=False, indent=1)[:7000])
    print(run.stderr[-2000:])


main()
