"""C-0173 kit: a picking order line bound to recipient version N stays valid after the recipient document moved to a later version
ONLY when the two accepted payloads are equal except topup_enabled/topup_horizon_days. New standalone function
RRL_TRADE_RECIPIENT_VERSION + RRL_TRADE_PICK_CONTEXT body uses it for both recipient reads. Reads live sources READ ONLY, asserted
edits, before/after SHA, apply/verify/rollback/rollback_verify and manifest. Nothing is applied."""
import hashlib, json, os, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-27_trade_recipient_version"); D.mkdir(parents=True, exist_ok=True)
NL = "\n"
TARGET = ("RRL_TRADE_PICK_CONTEXT", "PACKAGE BODY")
TRANSPORT = ("RRL_TRADE_TRANSPORT_CORE", "PACKAGE BODY")
FUNCTION = ("RRL_TRADE_RECIPIENT_VERSION", "FUNCTION")
DEPS = (("RRL_TRADE_PICK_CONTEXT", "PACKAGE"), ("RRL_TRADE_TRANSPORT_CORE", "PACKAGE"), ("RRL_TRADE_TOPUP_ADOPT", "PACKAGE"), ("RRL_TRADE_STOCK_GUARD", "PACKAGE"))
sha = lambda t: hashlib.sha256(t.encode()).hexdigest().upper()
src = {}
with OracleGateway().transaction("C-0173 kit sources READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in (TARGET, TRANSPORT, FUNCTION) + DEPS:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        src[(name, kind)] = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
    cur.execute("select count(*) from USER_OBJECTS where OBJECT_NAME=:n", n=FUNCTION[0]); assert cur.fetchone()[0] == 0, "function must be absent"
before = src[TARGET]

FUNC = """function RRL_TRADE_RECIPIENT_VERSION(p_ware number,p_recipient varchar2,p_bound number)return number is
 -- C-0173: the recipient version an order line bound to version p_bound may use now. The current accepted version itself, or null.
 -- A later version is compatible only when its accepted payload equals the bound version's accepted payload (RRL_TRADE_MESSAGE
 -- history) after removing ONLY topup_enabled and topup_horizon_days. Several accepted records of that version with the same content
 -- (a replay under a new event id) are one snapshot; records with differing content are ambiguous. Missing/ambiguous history: null.
 c_patch constant varchar2(100):='{"topup_enabled":null,"topup_horizon_days":null}';
 v_current number;v_body clob;v_old clob;n number:=0;v_equal number;
begin
 select VERSION_NO,BODY_JSON into v_current,v_body from RRL_TRADE_DOCUMENT
  where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=p_recipient and STATUS='ACCEPTED';
 if v_current=p_bound then return v_current;end if;
 if p_bound is null or v_current<p_bound then return null;end if;
 for m in(select json_query(REQUEST_JSON,'$.payload' returning clob)PAYLOAD from RRL_TRADE_MESSAGE
  where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=p_recipient and VERSION_NO=p_bound
   and json_value(RESULT_JSON,'$.status')='ACCEPTED' order by CREATED_AT fetch first 1 rows only)loop
  v_old:=m.PAYLOAD;
 end loop;
 if v_old is null then return null;end if;
 select count(*)into n from RRL_TRADE_MESSAGE where WARE_ID=p_ware and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=p_recipient and VERSION_NO=p_bound
  and json_value(RESULT_JSON,'$.status')='ACCEPTED'
  and(json_query(REQUEST_JSON,'$.payload' returning clob)is null or not json_equal(json_query(REQUEST_JSON,'$.payload' returning clob),v_old));
 if n<>0 then return null;end if;
 select case when json_equal(json_mergepatch(v_old,c_patch returning clob),json_mergepatch(v_body,c_patch returning clob))then 1 else 0 end into v_equal from dual;
 if v_equal=1 then return v_current;end if;
 return null;
exception when no_data_found then return null;
end;"""


def edit(text, old, new):
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new)


after = before
after = edit(after, "g_tx varchar2(100);g_valid boolean;", "g_tx varchar2(100);g_valid boolean;g_rver number;")
after = edit(after, "g_valid:=false;g_ware:=null;g_write:=1;end;", "g_valid:=false;g_ware:=null;g_write:=1;g_rver:=null;end;")
after = edit(after, " procedure enter_line(p_row number,p_actor varchar2)is n number;", " procedure enter_line(p_row number,p_actor varchar2)is n number;v_rid varchar2(100);v_rv number;")
after = edit(after, "   select WARE_ID into g_ware from RRL_TRADE_ORDER_LINK where CUSTOMER_ORDER_ID=g_line.CUSTOMER_ORDER_ID;",
             "   select WARE_ID,RECIPIENT_ID,RECIPIENT_VERSION into g_ware,v_rid,v_rv from RRL_TRADE_ORDER_LINK where CUSTOMER_ORDER_ID=g_line.CUSTOMER_ORDER_ID;")
after = edit(after, "  exception when no_data_found then return;end;\n  select count(*)into n from RRL_TRADE_ORDER_LINK l",
             "  exception when no_data_found then return;end;\n"
             "  -- C-0173: the bound recipient version, or a later one whose payload differs only in top-up settings; otherwise null (stale).\n"
             "  g_rver:=RRL_TRADE_RECIPIENT_VERSION(g_ware,v_rid,v_rv);\n"
             "  select count(*)into n from RRL_TRADE_ORDER_LINK l")
after = edit(after, "r.EXTERNAL_ID=l.RECIPIENT_ID and r.VERSION_NO=l.RECIPIENT_VERSION and r.STATUS='ACCEPTED'",
             "r.EXTERNAL_ID=l.RECIPIENT_ID and r.VERSION_NO=g_rver and r.STATUS='ACCEPTED'")
after = edit(after, "rd.EXTERNAL_ID=tl.RECIPIENT_ID and rd.VERSION_NO=tl.RECIPIENT_VERSION",
             "rd.EXTERNAL_ID=tl.RECIPIENT_ID and rd.VERSION_NO=g_rver")
after = edit(after, "s_tx varchar2(100):=g_tx;s_valid boolean:=g_valid;v varchar2(100);",
             "s_tx varchar2(100):=g_tx;s_valid boolean:=g_valid;s_rver number:=g_rver;v varchar2(100);")
after = edit(after, "g_tx:=s_tx;g_valid:=s_valid;end;", "g_tx:=s_tx;g_valid:=s_valid;g_rver:=s_rver;end;")
assert "l.RECIPIENT_VERSION" not in after and "tl.RECIPIENT_VERSION" not in after
t_before = src[TRANSPORT]
t_after = edit(t_before, "rd.EXTERNAL_ID=tl.RECIPIENT_ID and rd.VERSION_NO=tl.RECIPIENT_VERSION and rd.STATUS='ACCEPTED'",
               "rd.EXTERNAL_ID=tl.RECIPIENT_ID and rd.VERSION_NO=RRL_TRADE_RECIPIENT_VERSION(tl.WARE_ID,tl.RECIPIENT_ID,tl.RECIPIENT_VERSION) and rd.STATUS='ACCEPTED'")

KEY_T, KEY_F, KEY_X = "RRL_TRADE_PICK_CONTEXT:PACKAGE BODY", "RRL_TRADE_RECIPIENT_VERSION:FUNCTION", "RRL_TRADE_TRANSPORT_CORE:PACKAGE BODY"
BEFORE = {KEY_T: sha(before), KEY_X: sha(t_before)}
AFTER = {KEY_F: sha(FUNC), KEY_T: sha(after), KEY_X: sha(t_after)}
UNCHANGED = {f"{n}:{k}": sha(src[(n, k)]) for n, k in DEPS}
(D / "001_function.sql").write_text("create or replace " + FUNC + NL + "/" + NL, encoding="utf-8")
(D / "002_pick_context_body.sql").write_text("create or replace " + after + NL + "/" + NL, encoding="utf-8")
(D / "before_pick_context_body.sql").write_text("create or replace " + before + NL + "/" + NL, encoding="utf-8")
(D / "003_transport_core_body.sql").write_text("create or replace " + t_after + NL + "/" + NL, encoding="utf-8")
(D / "before_transport_core_body.sql").write_text("create or replace " + t_before + NL + "/" + NL, encoding="utf-8")
SAME = ("declare s clob;n number;" + NL + " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin" + NL
        + "  dbms_lob.createtemporary(s,true);" + NL
        + "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;" + NL
        + "  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;" + NL
        + "  dbms_lob.freetemporary(s);" + NL + " end;" + NL + "begin" + NL)
checks = lambda d, code: "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');" + NL for k, v in d.items())
INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
ABSENT = " select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TRADE_RECIPIENT_VERSION';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
END = "end;" + NL + "/" + NL
TGT = " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;" + NL
(D / "000_preflight.sql").write_text(SAME + TGT + checks(BEFORE, "BEFORE_SOURCE_DRIFT") + checks(UNCHANGED, "DEPENDENCY_DRIFT") + ABSENT.format("FUNCTION_ALREADY_EXISTS")
    + INVALID.format("INVALID_BEFORE") + END, encoding="utf-8")
(D / "verify.sql").write_text(SAME + checks(AFTER, "AFTER_SOURCE_MISMATCH") + checks(UNCHANGED, "DEPENDENCY_CHANGED") + INVALID.format("INVALID_OBJECTS")
    + " select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_PICK_CONTEXT','RRL_TRADE_RECIPIENT_VERSION','RRL_TRADE_TRANSPORT_CORE');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(BEFORE, "BEFORE_SOURCE_NOT_RESTORED") + checks(UNCHANGED, "DEPENDENCY_CHANGED")
    + ABSENT.format("FUNCTION_NOT_DROPPED") + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
MID, DESC = "2026-10-27-trade-recipient-version", "Pick context and trip demand accept a later recipient version differing only in top-up settings"
ledger = lambda status: (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
    + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
    + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
    + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)
(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_function.sql", "@@002_pick_context_body.sql", "@@003_transport_core_body.sql", "@@verify.sql"]) + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "declare begin" + TGT + "end;", "/",
    "-- Restore only over the exact candidate sources (no drift). Rolling back re-applies the stricter exact-version check: lines bound to an",
    "-- older recipient version become stale again; no stock, reservation or posting is changed by this kit or its rollback.",
    SAME + checks(AFTER, "AFTER_SOURCE_DRIFT_REFUSED") + checks(UNCHANGED, "DEPENDENCY_DRIFT_REFUSED") + END.rstrip(NL),
    "@@before_pick_context_body.sql", "@@before_transport_core_body.sql", "drop function RRL_TRADE_RECIPIENT_VERSION;", "@@rollback_verify.sql"]) + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
(D / "manifest.json").write_text(json.dumps({"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0173", "status": "NOT_APPLIED", "applied_by_claude": False,
    "new_objects": {KEY_F: AFTER[KEY_F]},
    "shared_objects_changed": {k: {"before_sha256": BEFORE[k], "after_sha256": AFTER[k]} for k in (KEY_T, KEY_X)},
    "before_sha256": BEFORE, "after_sha256": AFTER, "unchanged_dependency_sha256": UNCHANGED,
    "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}, indent=1), encoding="utf-8")
(D.parent.parent.parent / "reports/tradecase/2026-10-27/claude/C0173/function_source.sql").write_text(FUNC + NL, encoding="utf-8")
print(json.dumps({"before": BEFORE, "after": AFTER}, indent=1))
