"""C-0164 kit scripts: only new objects; the access/guard/outbox packages it calls are recorded by SHA as unchanged (preflight + verify)."""
import hashlib, json, os, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_composition_ack")
NL = "\n"


def objects(path):
    s = (D / path).read_text(encoding="utf-8").replace("\r\n", "\n")
    out = {}
    for part in re.split(r"\n/\n", s):
        part = part.strip("\n")
        m = re.search(r"create or replace (package body|package) (\w+)", part)
        if m:
            out[f"{m.group(2)}:{m.group(1).upper()}"] = hashlib.sha256(part[m.start() + len("create or replace "):].rstrip("\n").encode()).hexdigest().upper()
    return out


UNCHANGED = {}
with OracleGateway().transaction("C-0164 dependency SHA READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in (("RRL_ACCESS_API", "PACKAGE"), ("RRL_ACCESS_API", "PACKAGE BODY"), ("RRL_TRADE_STOCK_GUARD", "PACKAGE"),
                       ("RRL_TRADE_STOCK_GUARD", "PACKAGE BODY"), ("RRL_TRACEABILITY_API", "PACKAGE"), ("RRL_TRACEABILITY_API", "PACKAGE BODY"),
                       ("RRL_STOCK_PLAN_HELPER", "PACKAGE")):
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        text = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
        UNCHANGED[f"{name}:{kind}"] = hashlib.sha256(text.encode()).hexdigest().upper()
A = objects("002_composition_api.sql")
SAME = ("declare s clob;n number;" + NL + " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin" + NL
        + "  dbms_lob.createtemporary(s,true);" + NL
        + "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;" + NL
        + "  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;" + NL
        + "  dbms_lob.freetemporary(s);" + NL + " end;" + NL + "begin" + NL)


def checks(d, code):
    return "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');" + NL for k, v in d.items())


NEW = "('RRL_TRADE_ORDER_COMPOSITION','RRL_TRADE_COMPOSITION_ACK','RRL_TRADE_ORDER_COMP_CUR_UK','RRL_TRADE_COMP_ACK_APPEND','RRL_TRADE_ORDER_COMP_FROZEN','RRL_TRADE_COMPOSITION_API')"
INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
END = "end;" + NL + "/" + NL
(D / "000_preflight.sql").write_text(SAME + " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;" + NL
                                     + checks(UNCHANGED, "DEPENDENCY_DRIFT")
                                     + f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in{NEW};if n<>0 then raise_application_error(-20999,'COMPOSITION_OBJECT_EXISTS');end if;" + NL
                                     + INVALID.format("INVALID_BEFORE") + END, encoding="utf-8")
(D / "verify.sql").write_text(SAME + checks(A, "AFTER_SOURCE_MISMATCH") + checks(UNCHANGED, "DEPENDENCY_CHANGED")
                              + f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in{NEW};if n<>7 then raise_application_error(-20999,'COMPOSITION_OBJECT_MISSING');end if;" + NL
                              + INVALID.format("INVALID_OBJECTS")
                              + " select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_COMPOSITION_API','RRL_TRADE_COMP_ACK_APPEND','RRL_TRADE_ORDER_COMP_FROZEN');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(UNCHANGED, "DEPENDENCY_CHANGED")
                                       + f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in{NEW};if n<>0 then raise_application_error(-20999,'COMPOSITION_OBJECT_REMAINS');end if;" + NL
                                       + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
MID, DESC = "2026-10-23-trade-composition-ack", "Assembled order composition reported once with separate SAP and SKM acknowledgments"


def ledger(status):
    return (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
            + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
            + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
            + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)


(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_schema.sql", "@@002_composition_api.sql", "@@verify.sql"]) + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join([
    "whenever sqlerror exit failure rollback",
    "declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;", "/",
    "-- Reported compositions and acknowledgments are working history: once any exists the rollback refuses instead of deleting it.",
    "declare n number;begin select count(*)into n from RRL_TRADE_ORDER_COMPOSITION;if n<>0 then raise_application_error(-20999,'COMPOSITION_HISTORY_PRESENT');end if;end;", "/",
    "drop package RRL_TRADE_COMPOSITION_API;", "drop table RRL_TRADE_COMPOSITION_ACK purge;", "drop table RRL_TRADE_ORDER_COMPOSITION purge;",
    "@@rollback_verify.sql"]) + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
manifest = {"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0164", "status": "NOT_APPLIED", "applied_by_claude": False,
            "new_objects": ["RRL_TRADE_ORDER_COMPOSITION (+index RRL_TRADE_ORDER_COMP_CUR_UK, trigger RRL_TRADE_ORDER_COMP_FROZEN)",
                            "RRL_TRADE_COMPOSITION_ACK (+trigger RRL_TRADE_COMP_ACK_APPEND)", "RRL_TRADE_COMPOSITION_API"],
            "shared_objects_changed": {}, "unchanged_dependency_sha256": UNCHANGED, "after_sha256": A,
            "compile_evidence": "not compiled (new tables required); compose() ran unchanged READ ONLY on real CASE and full-pallet orders (reports/tradecase/2026-10-23/claude/C0164/candidate-live.json)",
            "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}
(D / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(A, indent=1))
