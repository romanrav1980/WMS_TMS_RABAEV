"""C-0160: preflight/verify/rollback/rollback_verify/apply/manifest for the trade pool eligibility kit (hashes from the kit files)."""
import hashlib, json, os, pathlib, re

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_pool_eligibility")
os.chdir(D)


def objects(path):
    s = (D / path).read_text(encoding="utf-8").replace("\r\n", "\n")
    out = {}
    for part in re.split(r"\n/\n", s):
        part = part.strip("\n")
        m = re.search(r"create or replace (package body|package) (\w+)", part)
        if m:
            out[f"{m.group(2)}:{m.group(1).upper()}"] = hashlib.sha256(part[m.start() + len("create or replace "):].rstrip("\n").encode()).hexdigest().upper()
    return out


B = {**objects("before_ctx_spec.sql"), **objects("before_ctx_body.sql"), **objects("before_pool_read.sql"), **objects("before_pool_cmd.sql")}
A = {**objects("001_ctx_spec.sql"), **objects("002_ctx_body.sql"), **objects("003_pool_read.sql"), **objects("004_pool_cmd.sql")}
LIVE = {"RRL_TRADE_PICK_CONTEXT:PACKAGE": "5BDC69384693B91FBECE9A5242B75E9C545BE77BA665398B4267B427E2B3B0B7",
        "RRL_TRADE_PICK_CONTEXT:PACKAGE BODY": "204D42072234011B1903806E97AA5279875C293AD6BB443ECD825A739EC3FC91",
        "RRL_STOCK_POOL_READ:PACKAGE BODY": "761B51CA2258159170DD40C50C988CAD6C1B706FE7577A31CD439C4A9DA126C1",
        "RRL_STOCK_POOL_CMD:PACKAGE BODY": "76AC3806FD7FF7C41D02B318D6A373694B3D364D36C7508C0162A6DE3621A6B3"}
assert B == LIVE, B
SAME = """declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
"""


def checks(d, code):
    return "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');\n" for k, v in d.items())


INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;\n"
(D / "000_preflight.sql").write_text(SAME + " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;\n"
                                     + checks(B, "SOURCE_DRIFT") + INVALID.format("INVALID_BEFORE") + "end;\n/\n", encoding="utf-8")
(D / "verify.sql").write_text(SAME + checks(A, "AFTER_SOURCE_MISMATCH") + INVALID.format("INVALID_OBJECTS")
                              + " select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_PICK_CONTEXT','RRL_STOCK_POOL_READ','RRL_STOCK_POOL_CMD');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;\nend;\n/\n", encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(B, "ROLLBACK_SOURCE_MISMATCH") + INVALID.format("INVALID_OBJECTS") + "end;\n/\n", encoding="utf-8")
# The context spec changes (accessible by + one function): its dependents are recompiled, only the invalid ones.
(D / "recompile.sql").write_text("begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;\n/\n", encoding="utf-8")
MID, DESC = "2026-10-23-trade-pool-eligibility", "Trade rows get common-pool shares only from compatible physical classes"


def ledger(status):
    return (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)\n"
            f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user\n"
            "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)\n"
            f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');\ncommit;\n")


(D / "apply.sql").write_text("whenever sqlerror exit failure rollback\n@@000_preflight.sql\n@@001_ctx_spec.sql\n@@002_ctx_body.sql\n@@003_pool_read.sql\n@@004_pool_cmd.sql\n@@recompile.sql\n@@verify.sql\n" + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text("whenever sqlerror exit failure rollback\n"
                                "declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;\n/\n"
                                "-- Package bodies/spec only, no data. Pool reservations created meanwhile stay as they are (SOFT, recalculated by the old pool).\n"
                                "@@before_pool_cmd.sql\n@@before_pool_read.sql\n@@before_ctx_spec.sql\n@@before_ctx_body.sql\n@@recompile.sql\n@@rollback_verify.sql\n" + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
manifest = {"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0160", "status": "NOT_APPLIED", "applied_by_claude": False,
            "shared_objects_changed": {
                "RRL_TRADE_PICK_CONTEXT (PACKAGE)": "+RRL_STOCK_POOL_READ in accessible by; +function compatible",
                "RRL_TRADE_PICK_CONTEXT (PACKAGE BODY)": "reason body moved to private check_source(p_access); reason=check_source(true); compatible=enter_line+check_source(false) with the caller's context restored",
                "RRL_STOCK_POOL_READ (PACKAGE BODY)": "trade site only: physical classes from sources whose only remaining reason is TRADE_ORDER_BINDING_REQUIRED; per-row compatible classes or pool_reason; bound 2000 pairs; non-trade snapshot byte-identical",
                "RRL_STOCK_POOL_CMD (PACKAGE BODY)": "trade plan proof (row x class shares) in compile; operate right on each used class owner in execute"},
            "before_sha256": B, "after_sha256": A,
            "evidence": "reports/tradecase/2026-10-23/claude/C0160/candidate-live.json (READ ONLY anonymous blocks)",
            "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}
(D / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(A, indent=1))
