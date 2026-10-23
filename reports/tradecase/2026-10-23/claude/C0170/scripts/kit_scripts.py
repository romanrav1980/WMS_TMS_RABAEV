"""C-0170 kit (candidate until the guard body reservation is confirmed): RRL_TRADE_STOCK_GUARD body gains a CASE_SHORT_APPROVE branch so a
picking shortage on trade stock can be decided through the existing writer. Reads the live body READ ONLY, one asserted edit, writes
before/after with SHA, apply/verify/rollback/rollback_verify and manifest. Nothing is applied."""
import hashlib, json, os, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_short_guard"); D.mkdir(parents=True, exist_ok=True)
NL = "\n"
TARGET = ("RRL_TRADE_STOCK_GUARD", "PACKAGE BODY")
DEPS = (("RRL_TRADE_STOCK_GUARD", "PACKAGE"), ("RRL_TRADE_PICK_CONTEXT", "PACKAGE"), ("RRL_STOCK_CASE_SHORT_CMD", "PACKAGE BODY"),
        ("RRL_STOCK_SHORT_RECOVERY", "PACKAGE BODY"))
sha = lambda t: hashlib.sha256(t.encode()).hexdigest().upper()
src = {}
with OracleGateway().transaction("C-0170 kit sources READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in (TARGET,) + DEPS:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        src[(name, kind)] = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
before = src[TARGET]
anchor = "   elsif command_kind not in('SAP_RECEIPT','RECEIPT_REVERSE',"
assert before.count(anchor) == 1
BRANCH = """   elsif command_kind='CASE_SHORT_APPROVE' then
    -- C-0170: a picking shortage decision on trade stock. The short binds the pallet to its own CASE line and pick task. Releasing the
    -- line's own reservation (ACCEPT_SHORT/RESTORE/WEIGHT_TOLERANCE) needs only that binding; READY moves replenished stock under the
    -- line, so the stock must be compatible with the order row by the same trade rules as a pick. Owner operate rights are checked below.
    declare v_short number:=src.get_number('short_id');v_decision varchar2(20):=nvl(metadata_value.get_string('decision'),'ACCEPT_SHORT');begin
     select l.PICK_TASK_ID into v_pick_task from RRL_CASE_PICK_SHORT s join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=s.CASE_PICK_LINE_ID
      join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where s.CASE_PICK_SHORT_ID=v_short and ct.WARE_ID=w.WARE_ID;
     if v_decision='READY'then
      select CELL into v_from from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
      RRL_TRADE_PICK_CONTEXT.enter_pick_task(v_pick_task,p_actor);
      v_reason:=reason(p_uid,v_from,w.WARE_ID,'PICK');RRL_TRADE_PICK_CONTEXT.clear_line;
      if v_reason is not null then fail(v_reason);end if;
     else
      select count(*)into n from RRL_STOCK_RESERVATION sr where sr.UID_PALLET=p_uid and sr.SOURCE_DOC_TYPE='PICK_WAVE'and sr.SOURCE_LINE_ID=v_pick_task
       and sr.RESERVATION_KIND='HARD'and sr.STATUS in('ACTIVE','ALLOCATED','PICKING');
      if n=0 then fail('TRADE_SHORT_BINDING_REQUIRED');end if;
     end if;
    exception when no_data_found then RRL_TRADE_PICK_CONTEXT.clear_line;fail('TRADE_SHORT_BINDING_REQUIRED');
    end;
"""
after = before.replace(anchor, BRANCH + anchor)
BEFORE, AFTER = {"RRL_TRADE_STOCK_GUARD:PACKAGE BODY": sha(before)}, {"RRL_TRADE_STOCK_GUARD:PACKAGE BODY": sha(after)}
UNCHANGED = {f"{n}:{k}": sha(src[(n, k)]) for n, k in DEPS}
(D / "001_guard_body.sql").write_text("create or replace " + after + NL + "/" + NL, encoding="utf-8")
(D / "before_guard_body.sql").write_text("create or replace " + before + NL + "/" + NL, encoding="utf-8")
SAME = ("declare s clob;n number;" + NL + " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin" + NL
        + "  dbms_lob.createtemporary(s,true);" + NL
        + "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;" + NL
        + "  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;" + NL
        + "  dbms_lob.freetemporary(s);" + NL + " end;" + NL + "begin" + NL)
checks = lambda d, code: "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');" + NL for k, v in d.items())
INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
END = "end;" + NL + "/" + NL
TGT = " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;" + NL
(D / "000_preflight.sql").write_text(SAME + TGT + checks(BEFORE, "BEFORE_SOURCE_DRIFT") + checks(UNCHANGED, "DEPENDENCY_DRIFT") + INVALID.format("INVALID_BEFORE") + END, encoding="utf-8")
(D / "verify.sql").write_text(SAME + checks(AFTER, "AFTER_SOURCE_MISMATCH") + checks(UNCHANGED, "DEPENDENCY_CHANGED") + INVALID.format("INVALID_OBJECTS")
    + " select count(*)into n from USER_ERRORS where NAME='RRL_TRADE_STOCK_GUARD';if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(BEFORE, "BEFORE_SOURCE_NOT_RESTORED") + checks(UNCHANGED, "DEPENDENCY_CHANGED") + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
MID, DESC = "2026-10-23-trade-short-guard", "Trade stock guard admits CASE_SHORT_APPROVE bound to its own CASE line"
ledger = lambda status: (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
    + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
    + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
    + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)
(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_guard_body.sql", "@@verify.sql"]) + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "declare begin" + TGT + "end;", "/",
    "-- Body only: no schema or data; restoring the previous body is always safe.", "@@before_guard_body.sql", "@@rollback_verify.sql"]) + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
(D / "manifest.json").write_text(json.dumps({"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0170", "status": "NOT_APPLIED", "applied_by_claude": False,
    "shared_objects_changed": {"RRL_TRADE_STOCK_GUARD:PACKAGE BODY": {"before_sha256": BEFORE["RRL_TRADE_STOCK_GUARD:PACKAGE BODY"], "after_sha256": AFTER["RRL_TRADE_STOCK_GUARD:PACKAGE BODY"]}},
    "before_sha256": BEFORE, "after_sha256": AFTER, "unchanged_dependency_sha256": UNCHANGED,
    "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}, indent=1), encoding="utf-8")
print(json.dumps({"before": BEFORE, "after": AFTER}, indent=1))
