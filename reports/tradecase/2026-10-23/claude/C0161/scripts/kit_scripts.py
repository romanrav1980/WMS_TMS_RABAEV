"""C-0161: preflight/verify/rollback/rollback_verify/apply/manifest for the trade pool eligibility kit (hashes from the kit files)."""
import hashlib, json, os, pathlib, re

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_topup_after_load")
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


B = {**objects("before_read_spec.sql"), **objects("before_read_body.sql"), **objects("before_api_body.sql"), **objects("before_cmd_body.sql")}
A = {**objects("001_read_spec.sql"), **objects("002_read_body.sql"), **objects("003_api_body.sql"), **objects("004_cmd_body.sql")}
LIVE = {"RRL_TRADE_TOPUP_READ:PACKAGE": "2904D679E038FAB7FDF31A36F80FE03665E9AD97B9B93A1ED09ED322EC61AD60",
        "RRL_TRADE_TOPUP_READ:PACKAGE BODY": "FA3BFC05C765A276E6653FB0F7D20537640F3AAF8A072D1AF0E9FC82C1F468FB",
        "RRL_TRADE_TOPUP_API:PACKAGE BODY": "1B2A60FD3A362E7865D6E368D20D7404D6CDFE0D93F4F05932EADB4B99F6C17B",
        "RRL_TRADE_TOPUP_CMD:PACKAGE BODY": "B5C54B308B3A3D97149FA40E36E93A2CD68E54DA35FA6C1D60856278CA6051F1"}
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
                              + " select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_TOPUP_READ','RRL_TRADE_TOPUP_API','RRL_TRADE_TOPUP_CMD');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;\nend;\n/\n", encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(B, "ROLLBACK_SOURCE_MISMATCH") + INVALID.format("INVALID_OBJECTS") + "end;\n/\n", encoding="utf-8")
# The read spec gains one function: its dependents (topup API/CMD and others) are recompiled, only the invalid ones.
(D / "recompile.sql").write_text("begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;\n/\n", encoding="utf-8")
MID, DESC = "2026-10-23-topup-after-load", "Top-up allowed with main cargo loaded; refused after departure; confirm serialized with LOAD/DEPART"


def ledger(status):
    return (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)\n"
            f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user\n"
            "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)\n"
            f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');\ncommit;\n")


(D / "apply.sql").write_text("whenever sqlerror exit failure rollback\n@@000_preflight.sql\n@@001_read_spec.sql\n@@002_read_body.sql\n@@003_api_body.sql\n@@004_cmd_body.sql\n@@recompile.sql\n@@verify.sql\n" + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text("whenever sqlerror exit failure rollback\n"
                                "declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;\n/\n"
                                "-- Package spec/bodies only, no data. Proposals saved meanwhile carry the new basis and must be recalculated under the old one.\n"
                                "@@before_cmd_body.sql\n@@before_api_body.sql\n@@before_read_spec.sql\n@@before_read_body.sql\n@@recompile.sql\n@@rollback_verify.sql\n" + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
manifest = {"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0161", "status": "NOT_APPLIED", "applied_by_claude": False,
            "shared_objects_changed": {
                "RRL_TRADE_TOPUP_READ (PACKAGE)": "+function departed",
                "RRL_TRADE_TOPUP_READ (PACKAGE BODY)": "trip_basis includes the native task vehicle and every load fact (op/status/content version); departed() = departed fact or applied TRIP_DEPART",
                "RRL_TRADE_TOPUP_API (PACKAGE BODY)": "save: TOPUP_LOADING_ALREADY_STARTED replaced by TOPUP_TRIP_DEPARTED",
                "RRL_TRADE_TOPUP_CMD (PACKAGE BODY)": "common_plan takes ROW RRL_TRANSPORT_TASK of the bound native task (as LOAD/DEPART); confirm refuses only after departure"},
            "before_sha256": B, "after_sha256": A,
            "evidence": "reports/tradecase/2026-10-23/claude/C0161/candidate-live.json (READ ONLY anonymous blocks)",
            "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}
(D / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(A, indent=1))
