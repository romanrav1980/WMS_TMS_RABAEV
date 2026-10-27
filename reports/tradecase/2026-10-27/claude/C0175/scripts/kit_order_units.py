"""C-0175 kit: ORDER lines normalized at intake may be non-executable (quantity 0 with normalization.executable=false: zero after
rounding, missing coefficient or setting). Native intake keeps them only with quantity 0, a TRIP may not assign them, and order
binding maps only executable lines. Reads live sources READ ONLY, asserted edits, before/after SHA, apply/verify/rollback.
Nothing is applied."""
import hashlib, json, os, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-27_trade_order_units"); D.mkdir(parents=True, exist_ok=True)
NL = "\n"
DOC, ORD = ("RRL_TRADE_DOCUMENT_API", "PACKAGE BODY"), ("RRL_TRADE_ORDER_API", "PACKAGE BODY")
DEPS = (("RRL_TRADE_DOCUMENT_API", "PACKAGE"), ("RRL_TRADE_ORDER_API", "PACKAGE"))
sha = lambda t: hashlib.sha256(t.encode()).hexdigest().upper()
src = {}
with OracleGateway().transaction("C-0175 kit sources READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in (DOC, ORD) + DEPS:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        src[(name, kind)] = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")

INERT = (" -- C-0175: an ORDER line kept by the order-unit normalization without an executable quantity (zero after rounding, missing\n"
         " -- coefficient or setting). It is stored with quantity 0, never bound to a warehouse row and never assigned to a trip.\n"
         " function inert(v json_object_t) return boolean is n json_object_t;\n"
         " begin\n"
         "  if v is null or not v.has('normalization') then return false;end if;\n"
         "  n:=treat(v.get('normalization') as json_object_t);\n"
         "  return n.has('executable') and n.get_boolean('executable') = false;\n"
         " end;\n")


def edit(text, old, new):
    assert text.count(old) == 1, old[:90]
    return text.replace(old, new)


doc = src[DOC]
doc = edit(doc, " procedure fail(p_reason varchar2) is begin raise_application_error(-20901,p_reason);end;",
           " procedure fail(p_reason varchar2) is begin raise_application_error(-20901,p_reason);end;\n" + INERT.rstrip("\n"))
doc = edit(doc, "    if v.get_number('quantity')<=0 or trunc(v.get_number('quantity'))<>v.get_number('quantity') then fail('WHOLE_UNIT_REQUIRED');end if;",
           "    if inert(v) then\n"
           "     if v.get_number('quantity')<>0 then fail('NON_EXECUTABLE_LINE_QUANTITY_MUST_BE_ZERO');end if;\n"
           "    elsif v.get_number('quantity')<=0 or trunc(v.get_number('quantity'))<>v.get_number('quantity') then fail('WHOLE_UNIT_REQUIRED');end if;")
doc = edit(doc, "      found:=true;qty:=v.get_number('quantity');",
           "      found:=true;qty:=v.get_number('quantity');\n"
           "      if inert(s) then fail('ORDER_LINE_NOT_EXECUTABLE');end if;")

ordr = src[ORD]
ordr = edit(ordr, " procedure fail(p_code varchar2)is begin raise_application_error(-20912,p_code);end;\n",
            " procedure fail(p_code varchar2)is begin raise_application_error(-20912,p_code);end;\n" + INERT)
ordr = edit(ordr, "f json_array_t:=json_array_t();r json_array_t:=json_array_t();outbox_id number;v_actor varchar2(50):=p_actor;",
            "f json_array_t:=json_array_t();r json_array_t:=json_array_t();outbox_id number;v_actor varchar2(50):=p_actor;v_exec number:=0;")
ordr = edit(ordr, "  select count(*)into n from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=v_native and STATUS<>'CANCELLED';\n"
                  "  if n<>rows_json.get_size or n<>maps.get_size or n<1 or n>200 then fail('TRADE_ORDER_LINE_SET_MISMATCH');end if;",
            "  for i in 0..rows_json.get_size-1 loop if not inert(treat(rows_json.get(i)as json_object_t))then v_exec:=v_exec+1;end if;end loop;\n"
            "  select count(*)into n from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=v_native and STATUS<>'CANCELLED';\n"
            "  -- C-0175: only executable lines have warehouse rows; a document without one is not bound (no wave, no reservation).\n"
            "  if n<>v_exec or n<>maps.get_size or n<1 or n>200 then fail('TRADE_ORDER_LINE_SET_MISMATCH');end if;")
ordr = edit(ordr, "   line:=treat(rows_json.get(i)as json_object_t);v_line:=line.get_string('line_id');matched:=false;",
            "   line:=treat(rows_json.get(i)as json_object_t);v_line:=line.get_string('line_id');matched:=false;\n"
            "   continue when inert(line);")

KD, KO = "RRL_TRADE_DOCUMENT_API:PACKAGE BODY", "RRL_TRADE_ORDER_API:PACKAGE BODY"
BEFORE = {KD: sha(src[DOC]), KO: sha(src[ORD])}
AFTER = {KD: sha(doc), KO: sha(ordr)}
UNCHANGED = {f"{n}:{k}": sha(src[(n, k)]) for n, k in DEPS}
for name, text in (("001_document_api_body.sql", doc), ("002_order_api_body.sql", ordr),
                   ("before_document_api_body.sql", src[DOC]), ("before_order_api_body.sql", src[ORD])):
    (D / name).write_text("create or replace " + text + NL + "/" + NL, encoding="utf-8")
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
    + " select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_DOCUMENT_API','RRL_TRADE_ORDER_API');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(BEFORE, "BEFORE_SOURCE_NOT_RESTORED") + checks(UNCHANGED, "DEPENDENCY_CHANGED") + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
MID, DESC = "2026-10-27-trade-order-units", "Trade ORDER keeps non-executable normalized lines; trips refuse and binding skips them"
ledger = lambda status: (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
    + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
    + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
    + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)
HISTORY = ("declare n number;begin" + NL
    + " -- Accepted ORDER documents with non-executable lines exist only under this kit; the previous bodies would reject their next version." + NL
    + " select count(*)into n from RRL_TRADE_DOCUMENT where ENTITY_TYPE='ORDER'and STATUS='ACCEPTED'" + NL
    + "  and json_exists(BODY_JSON,'$.lines[*]?(@.normalization.executable == false)');" + NL
    + " if n<>0 then raise_application_error(-20999,'TRADE_ORDER_UNIT_HISTORY_PRESENT');end if;" + NL + "end;" + NL + "/")
(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_document_api_body.sql", "@@002_order_api_body.sql", "@@verify.sql"]) + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "declare begin" + TGT + "end;", "/",
    "-- Restore only over the exact candidate bodies (no drift) and only before any ORDER with a non-executable line was accepted.",
    SAME + checks(AFTER, "AFTER_SOURCE_DRIFT_REFUSED") + checks(UNCHANGED, "DEPENDENCY_DRIFT_REFUSED") + END.rstrip(NL), HISTORY,
    "@@before_document_api_body.sql", "@@before_order_api_body.sql", "@@rollback_verify.sql"]) + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
(D / "manifest.json").write_text(json.dumps({"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0175", "status": "NOT_APPLIED", "applied_by_claude": False,
    "shared_objects_changed": {k: {"before_sha256": BEFORE[k], "after_sha256": AFTER[k]} for k in (KD, KO)},
    "before_sha256": BEFORE, "after_sha256": AFTER, "unchanged_dependency_sha256": UNCHANGED,
    "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}, indent=1), encoding="utf-8")
print(json.dumps({"before": BEFORE, "after": AFTER}, indent=1))
