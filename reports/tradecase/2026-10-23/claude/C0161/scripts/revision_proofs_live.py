"""C-0161 revision proofs, READ ONLY anonymous blocks on the live DB (no writes):
1) basis folding: the candidate's chained SHA over 3000 synthetic load transitions (~200K chars) fits; the old plain concatenation
   overflows (ORA-06502) on the same input; folding is order-sensitive and deterministic;
2) departure at confirmation: the candidate predicate (json_value ... returning timestamp with time zone error on error) on the real
   accepted TRIP documents, and at the boundary: planned departure 1 s ahead → allowed, 1 s behind → TOPUP_DEPARTURE_TIME_PASSED,
   unreadable value → TOPUP_DEPARTURE_TIME_INVALID."""
import json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
K = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_topup_after_load")
NL = "\n"
read = (K / "002_read_body.sql").read_text(encoding="utf-8")
SHA = read[read.index(" function sha("):read.index(" function trip_basis(")]
cmd = (K / "004_cmd_body.sql").read_text(encoding="utf-8")
assert "returning timestamp with time zone error on error" in cmd and "dep<=systimestamp then fail('TOPUP_DEPARTURE_TIME_PASSED')" in cmd
out = {}
with OracleGateway().transaction("C-0161 revision proofs READ ONLY") as cur:
    cur.execute("set transaction read only")
    fold = ("declare acc varchar2(32767):='TRIP:1';lh varchar2(64):='-';cnt number:=0;" + NL + SHA + NL
            + "begin for i in 1..3000 loop lh:=sha(lh||'|L:'||'LOAD.OPERATION.'||lpad(i,8,'0')||'.'||rpad('X',30,'X')||':LOADED:'||mod(i,7));cnt:=cnt+1;end loop;"
            + "acc:=acc||'|T:33665:TRUCK:'||cnt||':'||lh;:len:=length(acc);:h:=sha(acc);end;")
    n, h = cur.var(oracledb.DB_TYPE_NUMBER), cur.var(oracledb.DB_TYPE_VARCHAR)
    cur.execute(fold, len=n, h=h); out["folded"] = {"transitions": 3000, "input_chars_approx": 3000 * 62, "acc_length": int(n.getvalue()), "basis": h.getvalue()}
    h2 = cur.var(oracledb.DB_TYPE_VARCHAR); cur.execute(fold, len=cur.var(oracledb.DB_TYPE_NUMBER), h=h2); out["folded"]["deterministic"] = h2.getvalue() == h.getvalue()
    swapped = fold.replace("mod(i,7)", "mod(3001-i,7)")
    h3 = cur.var(oracledb.DB_TYPE_VARCHAR); cur.execute(swapped, len=cur.var(oracledb.DB_TYPE_NUMBER), h=h3); out["folded"]["order_or_status_change_changes_basis"] = h3.getvalue() != h.getvalue()
    plain = ("declare acc varchar2(32767):='TRIP:1';begin for i in 1..3000 loop acc:=acc||'|L:'||'LOAD.OPERATION.'||lpad(i,8,'0')||'.'||rpad('X',30,'X')||':LOADED:'||mod(i,7);end loop;end;")
    try:
        cur.execute(plain); out["plain_concatenation"] = "NO_ERROR"
    except oracledb.DatabaseError as e:
        out["plain_concatenation"] = str(e.args[0]).split(NL)[0]
    print(out)

    pred = ("declare dep timestamp with time zone;r varchar2(100);begin"
            " begin select json_value(:doc,'$.planned_departure_at'returning timestamp with time zone error on error)into dep from dual;"
            " if dep is null or dep<=systimestamp then r:='TOPUP_DEPARTURE_TIME_PASSED';else r:='ALLOWED';end if;"
            " exception when others then r:='TOPUP_DEPARTURE_TIME_INVALID';end; :r:=r;end;")

    def check(doc):
        r = cur.var(oracledb.DB_TYPE_VARCHAR); cur.execute(pred, doc=doc, r=r); return r.getvalue()
    cur.execute("select to_char(systimestamp at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.FF6')||'+00:00' from dual")
    now = cur.fetchone()[0]
    cur.execute("select to_char(systimestamp at time zone 'UTC'+interval '1' second,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6')||'+00:00',"
                "to_char(systimestamp at time zone 'UTC'-interval '1' second,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6')||'+00:00' from dual")
    ahead, behind = cur.fetchone()
    out["boundary"] = {"save_before_departure_now+1s": check(json.dumps({"planned_departure_at": ahead})),
                       "confirm_after_departure_now-1s": check(json.dumps({"planned_departure_at": behind})),
                       "missing": check("{}"), "unreadable": check(json.dumps({"planned_departure_at": "tomorrow"}))}
    cur.execute("select EXTERNAL_ID,BODY_JSON from RRL_TRADE_DOCUMENT where ENTITY_TYPE='TRIP' and STATUS='ACCEPTED' order by CHANGED_AT desc fetch first 5 rows only")
    out["real_trips"] = {}
    for ext, body in cur.fetchall():
        text = body.read() if hasattr(body, "read") else body
        out["real_trips"][ext] = {"planned_departure_at": json.loads(text).get("planned_departure_at"), "result": check(text)}
    print(out["boundary"]); print(out["real_trips"])
pathlib.Path(__file__).parent.parent.joinpath("revision-proofs-live.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
