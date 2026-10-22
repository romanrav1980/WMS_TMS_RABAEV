"""Generate preflight/verify/apply/rollback/manifest for 2026-10-22_trade_topup_proposal.

Hashes follow the existing migrations: sha256 of USER_SOURCE text joined, CR removed, trailing LF trimmed.
Before-hashes come from the before_*.sql files (exact dumps), after-hashes from the patched files.
"""
import hashlib
import json
import pathlib

M = pathlib.Path(r"C:\projects\TMS\db\migrations\2026-10-22_trade_topup_proposal")
MID = "2026-10-22-trade-topup-proposal"
DESC = "Durable top-up proposals, atomic hold+SAP request confirmation, own release, wave adoption gate"
# (object, type, before file, after file)
SHARED = [
    ("RRL_STOCK_POSTING_API", "PACKAGE BODY", "before_rrl_stock_posting_api.sql", "005_posting_api.sql", None),
    ("RRL_TRADE_STOCK_GUARD", "PACKAGE BODY", "before_rrl_trade_stock_guard.sql", "006_trade_guard.sql", None),
    ("RRL_TRADE_PICK_CONTEXT", "PACKAGE BODY", "before_rrl_trade_pick_context.sql", "007_pick_context.sql", None),
    ("RRL_STOCK_RESERVE_CORE", "PACKAGE", "before_rrl_stock_reserve_core_spec.sql", "008_core_access.sql", 0),
    ("RRL_STOCK_UNIT_CORE", "PACKAGE", "before_rrl_stock_unit_core_spec.sql", "008_core_access.sql", 1),
]
NEW_PACKAGES = ["RRL_TRADE_TOPUP_READ", "RRL_TRADE_TOPUP_API", "RRL_TRADE_TOPUP_CMD"]
NEW_TABLES = ["RRL_TRADE_TOPUP_EVENT", "RRL_TRADE_TOPUP_HOLD", "RRL_TRADE_TOPUP_DECISION", "RRL_TRADE_TOPUP_PROPOSAL"]


def stored_text(ddl: str) -> str:
    text = ddl.replace("\r", "")
    assert text.startswith("create or replace ") and text.rstrip().endswith("/"), ddl[:60]
    return text[len("create or replace "):].rstrip()[:-1].rstrip("\n")


def unit(file: str, index: int | None) -> str:
    raw = (M / file).read_text(encoding="utf-8")
    if index is None:
        return stored_text(raw)
    blocks = [b for b in raw.replace("\r", "").split("\n/\n") if b.strip()]
    return stored_text(blocks[index] + "\n/\n")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


before = {name: sha(unit(b, None)) for name, _, b, _, i in SHARED}
after = {name: sha(unit(a, i)) for name, _, _, a, i in SHARED}


def check_block(expect: dict[str, str], code: str) -> str:
    lines = ["declare s clob;", " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin",
             "  dbms_lob.createtemporary(s,true);",
             "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;",
             f"  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'{code}:'||p_name);end if;",
             "  dbms_lob.freetemporary(s);", " end;", "begin",
             " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;"]
    for name, typ, *_ in SHARED:
        lines.append(f" same('{name}','{typ}','{expect[name]}');")
    lines += ["end;", "/", ""]
    return "\n".join(lines)


preflight = check_block(before, "SOURCE_DRIFT") + (
    "declare n number;begin\n"
    f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in({','.join(repr(x) for x in NEW_PACKAGES + NEW_TABLES)},'RRL_TRADE_TOPUP_PROPOSAL_SQ');\n"
    " if n<>0 then raise_application_error(-20999,'TOPUP_OBJECTS_ALREADY_PRESENT');end if;\n"
    " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;\nend;\n/\n")
verify = check_block(after, "SOURCE_NOT_APPLIED") + (
    "declare n number;begin\n"
    " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;\n"
    f" select count(*)into n from USER_ERRORS where NAME in({','.join(repr(x) for x in NEW_PACKAGES + [s[0] for s in SHARED])});\n"
    " if n<>0 then raise_application_error(-20999,'TOPUP_COMPILE_ERRORS');end if;\n"
    f" select count(*)into n from USER_TABLES where TABLE_NAME in({','.join(repr(x) for x in NEW_TABLES)});if n<>4 then raise_application_error(-20999,'TOPUP_TABLES_MISSING');end if;\nend;\n/\n")
rollback_verify = check_block(before, "SOURCE_NOT_RESTORED") + (
    "declare n number;begin\n"
    " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;\n"
    f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in({','.join(repr(x) for x in NEW_PACKAGES + NEW_TABLES)},'RRL_TRADE_TOPUP_PROPOSAL_SQ');\n"
    " if n<>0 then raise_application_error(-20999,'TOPUP_OBJECTS_REMAIN');end if;\nend;\n/\n")
record = lambda status, script: (  # noqa: E731
    f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)\n"
    f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user\n"
    "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)\n"
    f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'{script}','rollback.sql','{status}');\ncommit;\n")
apply = ("whenever sqlerror exit failure rollback\n@@000_preflight.sql\n@@001_schema.sql\n@@008_core_access.sql\n@@002_read.sql\n@@003_api.sql\n"
         "@@004_cmd.sql\n@@005_posting_api.sql\n@@006_trade_guard.sql\n@@007_pick_context.sql\n@@verify.sql\n" + record("APPLIED", "apply.sql"))
rollback = ("whenever sqlerror exit failure rollback\n"
            "declare n number;begin\n"
            " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;\n"
            " -- Physical holds and decision history are business evidence: release/archive them first, never drop silently.\n"
            " select count(*)into n from RRL_TRADE_TOPUP_PROPOSAL;if n<>0 then raise_application_error(-20999,'TOPUP_DATA_PRESENT_RELEASE_AND_ARCHIVE_FIRST');end if;\n"
            "end;\n/\n"
            "@@before_rrl_trade_pick_context.sql\n@@before_rrl_trade_stock_guard.sql\n@@before_rrl_stock_posting_api.sql\n"
            "drop package RRL_TRADE_TOPUP_CMD;\ndrop package RRL_TRADE_TOPUP_API;\ndrop package RRL_TRADE_TOPUP_READ;\n"
            "@@before_rrl_stock_reserve_core_spec.sql\n@@before_rrl_stock_unit_core_spec.sql\n"
            + "".join(f"drop table {t} purge;\n" for t in NEW_TABLES) + "drop sequence RRL_TRADE_TOPUP_PROPOSAL_SQ;\n"
            "begin dbms_utility.compile_schema(user,false);end;\n/\n@@rollback_verify.sql\n" + record("ROLLED_BACK", "apply.sql"))
for name, text in {"000_preflight.sql": preflight, "verify.sql": verify, "rollback_verify.sql": rollback_verify,
                   "apply.sql": apply, "rollback.sql": rollback}.items():
    (M / name).write_text(text, encoding="utf-8", newline="")
combined = lambda d: hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()  # noqa: E731
(M / "manifest.json").write_text(json.dumps({"target": "RABAEV/orcl", "migration_id": MID, "before": combined(before), "after": combined(after),
                                             "objects_before": before, "objects_after": after,
                                             "new_objects": NEW_PACKAGES + NEW_TABLES + ["RRL_TRADE_TOPUP_PROPOSAL_SQ"],
                                             "applied_by_claude": False}, indent=1), encoding="utf-8", newline="")
print(json.dumps({"before": before, "after": after}, indent=1))
