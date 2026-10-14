# C-0020: собственные участники и UI-сценарий недостачи тары с независимым REJECT.
# Пароли читаются/создаются только в памяти и Oracle, передаются сценарию через stdin и не печатаются.
import json, secrets, subprocess, sys
from pathlib import Path

ROOT = Path("C:/projects/TMS")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
import oracledb, httpx
from stock_posting_environment import load_local_oracle_environment

load_local_oracle_environment()
from app.config import get_settings

s = get_settings()
OUT = Path(sys.argv[1]); STEP = sys.argv[2] if len(sys.argv) > 2 else "all"
CTX = json.loads((ROOT / "tmp/context1348.json").read_text(encoding="utf-8"))
APPROVER = "C0015_TARE_APPROVER"
APPROVER_GROUP = "C0015_TAREAPPR"  # USER_GROUP.ID ограничен 15 символами


def snapshot(c, tag):
    q = c.cursor()
    def rows(sql, **p):
        q.execute(sql, p); cols = [d[0].lower() for d in q.description]
        return [{k: (str(v) if v is not None else None) for k, v in zip(cols, r)} for r in q.fetchall()]
    res = {"tag": tag}
    res["balance"] = rows("select CONDITION_CODE,CUSTODIAN_KIND,CUSTODIAN_ID,to_char(QUANTITY,'TM9') QTY,BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=9807 and PALLET_TYPE_ID=1 order by 1,2,3")
    res["store_debt"] = rows("select CLAIM_KEY,CONDITION_CODE,to_char(OUTSTANDING_QTY,'TM9') OUTSTANDING from RRL_TARE_STORE_DEBT where OWNER_WARE_ID=9807 and PALLET_TYPE_ID=1 order by 2,1")
    res["resolutions"] = rows("select OPERATION_ID,RESOLUTION_KIND,CUSTODIAN_KIND,CUSTODIAN_ID,to_char(QUANTITY,'TM9') QTY,DAMAGE_OPERATION_ID,DELIVERY_ACCEPT_OPERATION_ID,DECISION_REFERENCE,ACTOR from RRL_TARE_RESOLUTION where OWNER_WARE_ID=9807 order by CREATED_AT")
    res["damage_positions"] = rows("select p.DAMAGE_OPERATION_ID,b.CUSTODIAN_KIND,b.CUSTODIAN_ID,to_char(p.QUANTITY,'TM9') QTY from RRL_TARE_DAMAGE_POSITION p join RRL_TARE_BALANCE b on b.BALANCE_KEY=p.BALANCE_KEY where b.OWNER_WARE_ID=9807")
    res["loss_claims"] = rows("""select c.OPERATION_ID,c.CONDITION_CODE,to_char(c.QUANTITY,'TM9') QTY,c.SOURCE_CLAIM_ID,c.DECISION_REFERENCE,c.ACTOR,b.CUSTODIAN_KIND,b.CUSTODIAN_ID,
        d.OPERATION_ID DECISION_OPERATION_ID,d.OUTCOME,d.ACTOR DECIDED_BY from RRL_TARE_LOSS_CLAIM c join RRL_TARE_BALANCE b on b.BALANCE_KEY=c.BALANCE_KEY
        left join RRL_TARE_LOSS_DECISION d on d.CLAIM_OPERATION_ID=c.OPERATION_ID where c.OWNER_WARE_ID=9807 order by c.CREATED_AT""")
    res["loss_decision_rows_per_claim"] = rows("select CLAIM_OPERATION_ID,count(*) N from RRL_TARE_LOSS_DECISION d where exists(select 1 from RRL_TARE_LOSS_CLAIM c where c.OPERATION_ID=d.CLAIM_OPERATION_ID and c.OWNER_WARE_ID=9807) group by CLAIM_OPERATION_ID")
    res["availability"] = rows("select to_char(PHYSICAL_QTY,'TM9') PHYSICAL,to_char(AVAILABLE_QTY,'TM9') AVAILABLE,to_char(LOSS_PENDING_QTY,'TM9') LOSS_PENDING from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=9807 and PALLET_TYPE_ID=1")
    res["offers_damaged"] = rows("""select o.OPERATION_ID,o.FROM_KIND,o.TO_KIND,to_char(o.QUANTITY,'TM9') QTY,o.OFFERED_BY,x.DAMAGE_OPERATION_ID,a.OPERATION_ID ACCEPT_OPERATION_ID,to_char(a.ACCEPTED_QTY,'TM9') ACCEPTED,a.ACCEPTED_BY
        from RRL_TARE_OFFER o left join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID left join RRL_TARE_DAMAGE_OFFER x on x.OFFER_OPERATION_ID=o.OPERATION_ID
        where o.TT_ID=33571 and o.CONDITION_CODE='DAMAGED' order by o.OFFERED_AT""")
    ops = [r["operation_id"] for r in res["loss_claims"]] + [r["decision_operation_id"] for r in res["loss_claims"] if r["decision_operation_id"]] + [r["operation_id"] for r in res["resolutions"]] + [r["operation_id"] for r in res["offers_damaged"]] + [r["accept_operation_id"] for r in res["offers_damaged"] if r["accept_operation_id"]]
    events = 0
    for op in ops:
        q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op", op=op); events += q.fetchone()[0]
    res["goods_events_for_these_operations"] = events
    return res


def fixture(c):
    q = c.cursor(); creds = {}
    for role, user in (("store", "OWN1348_STORE"), ("driver", "OWN1306_DRIVER"), ("admin", "admin")):
        q.execute("select PASS from RUSERS where ID=:u and nvl(DELETED,0)=0", u=user); creds[role] = {"username": user, "password": q.fetchone()[0]}
    q.execute("select count(*) from USER_GROUP where ID=:id", id=APPROVER_GROUP)
    if q.fetchone()[0] == 0:
        q.execute("insert into USER_GROUP(ID,NAME)values(:id,'Own C0015 independent tare write-off approver')", id=APPROVER_GROUP)
    secret = secrets.token_urlsafe(18)
    q.execute("select count(*) from RUSERS where ID=:id", id=APPROVER)
    if q.fetchone()[0] == 0:
        q.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED)values(:id,'Own C0015 tare approver',:p,:grp,9807,0)", id=APPROVER, grp=APPROVER_GROUP, p=secret)
    else:
        q.execute("update RUSERS set PASS=:p,WARE_ID=9807,DELETED=0 where ID=:id and USER_GROUP=:grp", id=APPROVER, grp=APPROVER_GROUP, p=secret)
    c.commit(); creds["approver"] = {"username": APPROVER, "password": secret}
    granted = {}
    with httpx.Client(base_url="http://127.0.0.1:8088", auth=("admin", creds["admin"]["password"]), timeout=30) as client:
        for group, rights in (("OWN1348_STORE", ["tare_loss_report"]), (APPROVER_GROUP, ["tare_view", "tare_writeoff", "wms_admin_login"])):
            have = {r["right1"].lower() for r in client.get(f"/api/admin/rights/groups/{group}/rights").json()}
            for right in rights:
                if right not in have:
                    client.post(f"/api/admin/rights/groups/{group}/rights", json={"right_name": right, "description": "Own C0020 dev tare loss fixture"}).raise_for_status()
            granted[group] = sorted(r["right1"] for r in client.get(f"/api/admin/rights/groups/{group}/rights").json())
    return creds, granted


with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
    before = snapshot(c, "before")
    creds, granted = fixture(c)
existing = next((c["operation_id"] for c in before["loss_claims"] if c["decision_reference"] == "DEV.C0020.LOSS-1"), "")
run = subprocess.run(["node", str(Path(__file__).with_name("c0020_ui_flow.cjs")), str(OUT), STEP, existing], input=json.dumps(creds), capture_output=True, text=True, encoding="utf-8")
for v in creds.values():
    assert v["password"] not in run.stdout and v["password"] not in run.stderr
with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
    after = snapshot(c, "after")
result = {"granted": granted, "before": before, "after": after, "ui_exit": run.returncode, "ui_stdout": run.stdout[-8000:], "ui_stderr": run.stderr[-3000:]}
(OUT.parent / "c0020_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"ui_exit": run.returncode, "granted": granted, "before_balance": before["balance"], "after": after}, ensure_ascii=False, indent=1)[:9000])
print(run.stdout[-4000:]); print(run.stderr[-2000:])
