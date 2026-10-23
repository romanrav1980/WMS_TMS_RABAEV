"""C-0162: preflight/verify/rollback/rollback_verify/recompile/apply/manifest for the trade pool access kit."""
import hashlib, json, os, pathlib, re

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_pool_access")


def objects(path):
    s = (D / path).read_text(encoding="utf-8").replace("\r\n", "\n")
    out = {}
    for part in re.split(r"\n/\n", s):
        part = part.strip("\n")
        m = re.search(r"create or replace (package body|package) (\w+)", part)
        if m:
            out[f"{m.group(2)}:{m.group(1).upper()}"] = hashlib.sha256(part[m.start() + len("create or replace "):].rstrip("\n").encode()).hexdigest().upper()
    return out


B = {**objects("before_pool_cmd_spec.sql"), **objects("before_pool_cmd_body.sql"), **objects("before_posting_api_body.sql")}
A = {**objects("001_pool_cmd_spec.sql"), **objects("002_pool_cmd_body.sql"), **objects("003_posting_api_body.sql")}
LIVE = {"RRL_STOCK_POOL_CMD:PACKAGE": "E1091C7662A9EFBE69E56CD6FF99CD783945B56C8F1B1CC75EC449DBE6DE57D9",
        "RRL_STOCK_POOL_CMD:PACKAGE BODY": "4ABD6C109C87870EF6D042B1F03D25FE7A60F64E7E58EB4A39DA1C45F4DE796F",
        "RRL_STOCK_POSTING_API:PACKAGE BODY": "6DAA16DD11152C696B6B20D5E10247BF59F36D2E94BB08489402516D0082BC81"}
assert B == LIVE, B
NL = "\n"
SAME = ("declare s clob;n number;" + NL
        + " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin" + NL
        + "  dbms_lob.createtemporary(s,true);" + NL
        + "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;" + NL
        + "  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;" + NL
        + "  dbms_lob.freetemporary(s);" + NL + " end;" + NL + "begin" + NL)


def checks(d, code):
    return "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');" + NL for k, v in d.items())


INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
END = "end;" + NL + "/" + NL
(D / "000_preflight.sql").write_text(SAME + " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;" + NL
                                     + checks(B, "SOURCE_DRIFT") + INVALID.format("INVALID_BEFORE") + END, encoding="utf-8")
(D / "verify.sql").write_text(SAME + checks(A, "AFTER_SOURCE_MISMATCH") + INVALID.format("INVALID_OBJECTS")
                              + " select count(*)into n from USER_ERRORS where NAME in('RRL_STOCK_POOL_CMD','RRL_STOCK_POSTING_API');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(B, "ROLLBACK_SOURCE_MISMATCH") + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
# The pool command spec gains assert_access: its dependents are recompiled, only the invalid ones.
(D / "recompile.sql").write_text("begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;" + NL + "/" + NL, encoding="utf-8")
MID, DESC = "2026-10-23-trade-pool-access", "Current warehouse/owner rights for the common pool, before committed replay too"


def ledger(status):
    return (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
            + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
            + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
            + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)


(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_pool_cmd_spec.sql", "@@002_pool_cmd_body.sql",
                                      "@@003_posting_api_body.sql", "@@recompile.sql", "@@verify.sql"]) + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join(["whenever sqlerror exit failure rollback",
                                         "declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;", "/",
                                         "-- Package spec/bodies only, no data.",
                                         "@@before_posting_api_body.sql", "@@before_pool_cmd_spec.sql", "@@before_pool_cmd_body.sql", "@@recompile.sql", "@@rollback_verify.sql"]) + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
manifest = {"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0162", "status": "NOT_APPLIED", "applied_by_claude": False,
            "shared_objects_changed": {
                "RRL_STOCK_POOL_CMD (PACKAGE)": "+procedure assert_access",
                "RRL_STOCK_POOL_CMD (PACKAGE BODY)": "require_edit = RRL_ACCESS_API.allowed(stock_reservation_edit, WAREHOUSE of the plan) instead of RRL_HAS_WRIGHT; assert_access = warehouse right + operate on owners of the recorded trade plan",
                "RRL_STOCK_POSTING_API (PACKAGE BODY)": "+1 line: RESERVATION_ALLOCATE_POOL calls RRL_STOCK_POOL_CMD.assert_access among the scope hooks before the committed-replay branch; posting, planning and locks of other commands unchanged"},
            "before_sha256": B, "after_sha256": A,
            "evidence": "reports/tradecase/2026-10-23/claude/C0162/candidate-live.json (READ ONLY anonymous blocks)",
            "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}
(D / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(A, indent=1))
