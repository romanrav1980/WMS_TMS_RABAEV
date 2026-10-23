"""C-0166 kit: inventory loss journal and restoration of the same marked units through the existing INVENTORY_COUNT writer.
Reads the current RRL_STOCK_UNIT_CORE spec/body and RRL_STOCK_INVENTORY_CMD body READ ONLY, keeps them as before_*.sql, applies narrow
textual edits (each asserted to match exactly once) and writes apply/verify/rollback with before/after SHA. Nothing is applied."""
import hashlib, json, os, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_inventory_found_units")
D.mkdir(parents=True, exist_ok=True)
NL = "\n"
CHANGED = (("RRL_STOCK_UNIT_CORE", "PACKAGE"), ("RRL_STOCK_UNIT_CORE", "PACKAGE BODY"), ("RRL_STOCK_INVENTORY_CMD", "PACKAGE BODY"))
DEPS = (("RRL_STOCK_INVENTORY_CMD", "PACKAGE"), ("RRL_STOCK_CTX_API", "PACKAGE"), ("RRL_STOCK_PLAN_HELPER", "PACKAGE"),
        ("RRL_STOCK_BALANCE_CORE", "PACKAGE"), ("RRL_STOCK_LOCK_API", "PACKAGE"), ("RRL_TRADE_STOCK_GUARD", "PACKAGE"))


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest().upper()


source = {}
with OracleGateway().transaction("C-0166 kit sources READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in CHANGED + DEPS:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        source[(name, kind)] = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
BEFORE = {f"{n}:{k}": sha(source[(n, k)]) for n, k in CHANGED}
UNCHANGED = {f"{n}:{k}": sha(source[(n, k)]) for n, k in DEPS}


def edit(text, old, new):
    assert text.count(old) == 1, (old[:80], text.count(old))
    return text.replace(old, new)


# --- RRL_STOCK_UNIT_CORE spec: one new procedure, same accessible-by list.
spec = edit(source[("RRL_STOCK_UNIT_CORE", "PACKAGE")], " procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob); ",
            " procedure issue_free_units(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob); \n"
            " -- C-0166: units of this lot/cell written off by an earlier INVENTORY_COUNT and found again, back to AVAILABLE (same key, same code).\n"
            " procedure restore_inventory_loss(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob); ")

# --- RRL_STOCK_UNIT_CORE body: the procedure, modelled on restore_issued; only an open inventory loss of the current INVENTORY_COUNT.
RESTORE = """ -- C-0166: only the current INVENTORY_COUNT may restore, only units of this lot/cell with an open inventory loss whose unit was not
 -- changed since (UNIT_VERSION recorded at the loss). A shipped or otherwise issued unit has no such loss and stays ISSUED.
 procedure restore_inventory_loss(p_uid varchar2,p_cell varchar2,p_qty number,p_units clob)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;v_expected number;v_distinct number;v_sum number:=0;v_remain number;v_live number;
 begin
  require_context;
  select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='INVENTORY_COUNT'and STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'INVENTORY_FOUND_PLAN_REQUIRED');end if;
  select count(*),count(distinct K)into v_expected,v_distinct from json_table(p_units,'$[*]'columns(K varchar2(64)path '$'));
  if v_expected<1 or v_expected>10000 or v_expected!=v_distinct then raise_application_error(-20884,'INVENTORY_FOUND_UNIT_SET_REQUIRED');end if;
  select nvl(max(REMAIN),0)into v_remain from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell;
  select nvl(sum(BASE_QTY),0)into v_live from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS!='ISSUED';
  if v_live!=v_remain then raise_application_error(-20884,'INVENTORY_FOUND_COMPOSITION_CONFLICT');end if;
  for k in(select j.K,u.PHYSICAL_UNIT_KEY,u.STOCK_STATUS,u.HARD_RESERVATION_ID,u.UNIT_VERSION,u.BASE_QTY,u.CURRENT_UID,u.CURRENT_CELL,
    (select max(l.UNIT_VERSION)keep(dense_rank last order by l.CREATED_AT)from RRL_INVENTORY_LOSS_UNIT l where l.PHYSICAL_UNIT_KEY=j.K and l.UID_PALLET=p_uid
      and l.CELL=p_cell and not exists(select 1 from RRL_INVENTORY_FOUND_UNIT f where f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID))LOSS_VERSION
   from json_table(p_units,'$[*]'columns(K varchar2(64)path '$'))j left join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K)loop
   if k.PHYSICAL_UNIT_KEY is null or k.CURRENT_UID!=p_uid or k.CURRENT_CELL!=p_cell then raise_application_error(-20884,'INVENTORY_FOUND_UNIT_NOT_IN_LOT');end if;
   if k.STOCK_STATUS!='ISSUED'or k.HARD_RESERVATION_ID is not null then raise_application_error(-20884,'INVENTORY_FOUND_UNIT_NOT_LOST');end if;
   if k.LOSS_VERSION is null then raise_application_error(-20886,'INVENTORY_FOUND_LOSS_REQUIRED');end if;
   if k.LOSS_VERSION!=k.UNIT_VERSION then raise_application_error(-20886,'INVENTORY_FOUND_UNIT_CHANGED_SINCE_LOSS');end if;
   own_unit(k.K);v_sum:=v_sum+k.BASE_QTY;
  end loop;
  if v_sum!=p_qty then raise_application_error(-20884,'INVENTORY_FOUND_QUANTITY_CONFLICT');end if;
  RRL_STOCK_CTX_API.begin_effect('UNIT',p_uid,p_cell);
  update RRL_WMS_RECEIPT_UNIT u set STOCK_STATUS='AVAILABLE',UNIT_VERSION=UNIT_VERSION+1
   where CURRENT_UID=p_uid and CURRENT_CELL=p_cell and STOCK_STATUS='ISSUED'
    and exists(select 1 from json_table(p_units,'$[*]'columns(K varchar2(64)path '$'))j where j.K=u.PHYSICAL_UNIT_KEY);
  if sql%rowcount!=v_expected then raise_application_error(-20890,'CLOSURE_CHANGED: inventory found units');end if;
  RRL_STOCK_CTX_API.end_effect;
 exception when others then RRL_STOCK_CTX_API.end_effect;raise;
 end;
"""
body = source[("RRL_STOCK_UNIT_CORE", "PACKAGE BODY")]
anchor = " procedure reserve_units(p_uid varchar2,p_cell varchar2,p_id number,p_qty number,p_units clob) is "
body = edit(body, anchor, RESTORE + anchor)

# --- RRL_STOCK_INVENTORY_CMD body.
inv = source[("RRL_STOCK_INVENTORY_CMD", "PACKAGE BODY")]
# compile: lock the found (ISSUED) units too; stock_closure locks only units that are not issued.
inv = edit(inv, "   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),article,x.get_string('cell'),null);",
           "   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),article,x.get_string('cell'),null);\n"
           "   if x.has('found_unit_keys') then declare g json_array_t:=x.get_array('found_unit_keys');begin\n"
           "    if g.get_size>10000 then raise_application_error(-20881,'INVENTORY_FOUND_UNIT_BOUND');end if;\n"
           "    for q in 0..g.get_size-1 loop RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',g.get_string(q));end loop;end;end if;")
inv = edit(inv, "units clob;revision_row number;", "units clob;found clob;lost clob;n_lost number;n_found number;revision_row number;")
inv = edit(inv, "   delta:=qty-p;eventid:=null;units:=null;",
           "   delta:=qty-p;eventid:=null;units:=null;found:=null;lost:=null;n_lost:=0;n_found:=0;\n"
           "   if sourcex.has('found_unit_keys') and sourcex.get_array('found_unit_keys').get_size>0 then found:=sourcex.get_array('found_unit_keys').to_clob;end if;")
inv = edit(inv, "    if marking!=0 then raise_application_error(-20884,'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS');end if;",
           "    -- C-0166: a marked increase is allowed only as the restoration of the same units lost by an earlier inventory count.\n"
           "    if marking!=0 and found is null then raise_application_error(-20884,'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS');end if;\n"
           "    if found is not null then\n"
           "     if units is not null then raise_application_error(-20884,'INVENTORY_FOUND_AND_LOST_SEPARATELY');end if;\n"
           "     -- Current owner operate right for every found unit, also when the lot remain is 0 (the trade guard walks only live units).\n"
           "     -- Fail closed: a found unit without trade attributes or in another warehouse is not restored.\n"
           "     declare v_cw number;v_cell4 varchar2(60):=x.get_string('cell');begin\n"
           "      select WARE_ID into v_cw from RRL_CELLS where CELL=v_cell4;\n"
           "      if v_cw!=ware then raise_application_error(-20887,'INVENTORY_FOUND_WAREHOUSE_CONFLICT');end if;\n"
           "      for o in(select j.K,a.OWNER_ID from json_table(found,'$[*]'columns(K varchar2(64)path '$'))j\n"
           "        left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=j.K)loop\n"
           "       if o.OWNER_ID is null then raise_application_error(-20882,'INVENTORY_FOUND_OWNER_REQUIRED');end if;\n"
           "       RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1);\n"
           "      end loop;end;\n"
           "     RRL_STOCK_UNIT_CORE.restore_inventory_loss(x.get_string('uid'),x.get_string('cell'),delta,found);\n"
           "     declare v_op varchar2(100):=d.get_string('operation_id');v_uid2 varchar2(200):=x.get_string('uid');v_cell2 varchar2(60):=x.get_string('cell');begin\n"
           "      insert into RRL_INVENTORY_FOUND_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID,FOUND_OPERATION_ID,REVISION_ID,UID_PALLET,CELL,ACTOR)\n"
           "       select l.PHYSICAL_UNIT_KEY,max(l.LOSS_OPERATION_ID)keep(dense_rank last order by l.CREATED_AT),v_op,doc,v_uid2,v_cell2,p_actor\n"
           "        from RRL_INVENTORY_LOSS_UNIT l join json_table(found,'$[*]'columns(K varchar2(64)path '$'))j on j.K=l.PHYSICAL_UNIT_KEY\n"
           "        where l.UID_PALLET=v_uid2 and l.CELL=v_cell2 and not exists(select 1 from RRL_INVENTORY_FOUND_UNIT f\n"
           "         where f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID)group by l.PHYSICAL_UNIT_KEY;\n"
           "      n_found:=sql%rowcount;end;\n"
           "    end if;")
inv = edit(inv, "   elsif delta<0 then\n\n    RRL_STOCK_UNIT_CORE.issue_free_units(x.get_string('uid'),x.get_string('cell'),-delta,units);",
           "   elsif delta<0 then\n\n"
           "    if found is not null then raise_application_error(-20884,'INVENTORY_FOUND_AND_LOST_SEPARATELY');end if;\n"
           "    -- C-0166: the exact units written off are journaled as an inventory loss (not a shipment), with their version after the write-off.\n"
           "    declare v_uid3 varchar2(200):=x.get_string('uid');v_cell3 varchar2(60):=x.get_string('cell');begin\n"
           "     select json_arrayagg(PHYSICAL_UNIT_KEY returning clob)into lost from RRL_WMS_RECEIPT_UNIT u where CURRENT_UID=v_uid3 and CURRENT_CELL=v_cell3\n"
           "      and STOCK_STATUS!='ISSUED'and(units is null or exists(select 1 from json_table(units,'$[*]'columns(K varchar2(64)path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));end;\n"
           "    RRL_STOCK_UNIT_CORE.issue_free_units(x.get_string('uid'),x.get_string('cell'),-delta,units);\n"
           "    if lost is not null then declare v_op varchar2(100):=d.get_string('operation_id');v_uid3 varchar2(200):=x.get_string('uid');v_cell3 varchar2(60):=x.get_string('cell');v_open number;begin\n"
           "     -- One open loss per unit: lost, found, then lost again is a new occurrence only after the previous one was recovered.\n"
           "     select count(*)into v_open from RRL_INVENTORY_LOSS_UNIT l join json_table(lost,'$[*]'columns(K varchar2(64)path '$'))j on j.K=l.PHYSICAL_UNIT_KEY\n"
           "      where not exists(select 1 from RRL_INVENTORY_FOUND_UNIT f where f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID);\n"
           "     if v_open>0 then raise_application_error(-20886,'INVENTORY_LOSS_ALREADY_OPEN');end if;\n"
           "     insert into RRL_INVENTORY_LOSS_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID,REVISION_ID,UID_PALLET,CELL,UNIT_VERSION,ACTOR)\n"
           "      select u.PHYSICAL_UNIT_KEY,v_op,doc,v_uid3,v_cell3,u.UNIT_VERSION,p_actor from RRL_WMS_RECEIPT_UNIT u\n"
           "       join json_table(lost,'$[*]'columns(K varchar2(64)path '$'))j on j.K=u.PHYSICAL_UNIT_KEY where u.STOCK_STATUS='ISSUED';\n"
           "     n_lost:=sql%rowcount;end;end if;")
inv = edit(inv, "fact.put('event_id',eventid);facts.append(fact);",
           "fact.put('event_id',eventid);fact.put('lost_units',n_lost);fact.put('found_units',n_found);facts.append(fact);")

AFTER_TEXT = {("RRL_STOCK_UNIT_CORE", "PACKAGE"): spec, ("RRL_STOCK_UNIT_CORE", "PACKAGE BODY"): body, ("RRL_STOCK_INVENTORY_CMD", "PACKAGE BODY"): inv}
AFTER = {f"{n}:{k}": sha(t) for (n, k), t in AFTER_TEXT.items()}
FILES = {("RRL_STOCK_UNIT_CORE", "PACKAGE"): "002_unit_core_spec.sql", ("RRL_STOCK_UNIT_CORE", "PACKAGE BODY"): "003_unit_core_body.sql",
         ("RRL_STOCK_INVENTORY_CMD", "PACKAGE BODY"): "004_inventory_cmd_body.sql"}
for key, name in FILES.items():
    (D / name).write_text("create or replace " + AFTER_TEXT[key] + NL + "/" + NL, encoding="utf-8")
    (D / ("before_" + name[4:])).write_text("create or replace " + source[key] + NL + "/" + NL, encoding="utf-8")

(D / "001_schema.sql").write_text("""-- C-0166: which marked units an inventory count wrote off, and which of exactly those were found again (append-only).
create table RRL_INVENTORY_LOSS_UNIT(
 PHYSICAL_UNIT_KEY varchar2(64)not null,LOSS_OPERATION_ID varchar2(100)not null,REVISION_ID number not null,UID_PALLET varchar2(200)not null,
 CELL varchar2(60)not null,UNIT_VERSION number not null,ACTOR varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_INV_LOSS_UNIT_PK primary key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID),
 constraint RRL_INV_LOSS_UNIT_KEY_FK foreign key(PHYSICAL_UNIT_KEY)references RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY),
 constraint RRL_INV_LOSS_UNIT_OP_FK foreign key(LOSS_OPERATION_ID)references RRL_STOCK_OPERATION(OPERATION_ID)
);
create index RRL_INV_LOSS_UNIT_LOT_IX on RRL_INVENTORY_LOSS_UNIT(UID_PALLET,CELL);
create table RRL_INVENTORY_FOUND_UNIT(
 PHYSICAL_UNIT_KEY varchar2(64)not null,LOSS_OPERATION_ID varchar2(100)not null,FOUND_OPERATION_ID varchar2(100)not null,REVISION_ID number not null,
 UID_PALLET varchar2(200)not null,CELL varchar2(60)not null,ACTOR varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_INV_FOUND_UNIT_PK primary key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID),
 constraint RRL_INV_FOUND_UNIT_LOSS_FK foreign key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID)references RRL_INVENTORY_LOSS_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID),
 constraint RRL_INV_FOUND_UNIT_OP_FK foreign key(FOUND_OPERATION_ID)references RRL_STOCK_OPERATION(OPERATION_ID)
);
create or replace trigger RRL_INV_LOSS_UNIT_APPEND before update or delete on RRL_INVENTORY_LOSS_UNIT
begin raise_application_error(-20863,'INVENTORY_LOSS_HISTORY_APPEND_ONLY');end;
/
create or replace trigger RRL_INV_FOUND_UNIT_APPEND before update or delete on RRL_INVENTORY_FOUND_UNIT
begin raise_application_error(-20863,'INVENTORY_FOUND_HISTORY_APPEND_ONLY');end;
/
""", encoding="utf-8")

SAME = ("declare s clob;n number;" + NL + " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin" + NL
        + "  dbms_lob.createtemporary(s,true);" + NL
        + "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;" + NL
        + "  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;" + NL
        + "  dbms_lob.freetemporary(s);" + NL + " end;" + NL + "begin" + NL)


def checks(d, code):
    return "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');" + NL for k, v in d.items())


NEW = "('RRL_INVENTORY_LOSS_UNIT','RRL_INVENTORY_FOUND_UNIT','RRL_INV_LOSS_UNIT_LOT_IX','RRL_INV_LOSS_UNIT_APPEND','RRL_INV_FOUND_UNIT_APPEND')"
INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
END = "end;" + NL + "/" + NL
TARGET = " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;" + NL
(D / "000_preflight.sql").write_text(SAME + TARGET + checks(BEFORE, "BEFORE_SOURCE_DRIFT") + checks(UNCHANGED, "DEPENDENCY_DRIFT")
    + f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in{NEW};if n<>0 then raise_application_error(-20999,'INVENTORY_FOUND_OBJECT_EXISTS');end if;" + NL
    + INVALID.format("INVALID_BEFORE") + END, encoding="utf-8")
# Dependents of UNIT_CORE spec recompile on use; compile them now so INVALID=0 is a real check.
RECOMPILE = "begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;" + NL + "/" + NL
(D / "verify.sql").write_text(SAME + checks(AFTER, "AFTER_SOURCE_MISMATCH") + checks(UNCHANGED, "DEPENDENCY_CHANGED")
    + f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in{NEW};if n<>5 then raise_application_error(-20999,'INVENTORY_FOUND_OBJECT_MISSING');end if;" + NL
    + INVALID.format("INVALID_OBJECTS")
    + " select count(*)into n from USER_ERRORS where NAME in('RRL_STOCK_UNIT_CORE','RRL_STOCK_INVENTORY_CMD');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(BEFORE, "BEFORE_SOURCE_NOT_RESTORED") + checks(UNCHANGED, "DEPENDENCY_CHANGED")
    + f" select count(*)into n from USER_OBJECTS where OBJECT_NAME in{NEW};if n<>0 then raise_application_error(-20999,'INVENTORY_FOUND_OBJECT_REMAINS');end if;" + NL
    + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
MID, DESC = "2026-10-23-inventory-found-units", "Inventory loss journal and restoration of the same marked units via INVENTORY_COUNT"


def ledger(status):
    return (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
            + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
            + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
            + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)


(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_schema.sql", "@@002_unit_core_spec.sql",
    "@@003_unit_core_body.sql", "@@004_inventory_cmd_body.sql"]) + NL + RECOMPILE + "@@verify.sql" + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join([
    "whenever sqlerror exit failure rollback",
    "declare begin" + TARGET + "end;", "/",
    "-- Recorded losses are working history: once any exists the rollback refuses instead of deleting it.",
    "declare n number;begin select count(*)into n from RRL_INVENTORY_LOSS_UNIT;if n<>0 then raise_application_error(-20999,'INVENTORY_LOSS_HISTORY_PRESENT');end if;end;", "/",
    "@@before_unit_core_spec.sql", "@@before_unit_core_body.sql", "@@before_inventory_cmd_body.sql",
    "drop table RRL_INVENTORY_FOUND_UNIT purge;", "drop table RRL_INVENTORY_LOSS_UNIT purge;"]) + NL + RECOMPILE + "@@rollback_verify.sql" + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
manifest = {"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0166", "status": "NOT_APPLIED", "applied_by_claude": False,
            "new_objects": ["RRL_INVENTORY_LOSS_UNIT (+index RRL_INV_LOSS_UNIT_LOT_IX, trigger RRL_INV_LOSS_UNIT_APPEND)",
                            "RRL_INVENTORY_FOUND_UNIT (+trigger RRL_INV_FOUND_UNIT_APPEND)"],
            "shared_objects_changed": {k: {"before_sha256": BEFORE[k], "after_sha256": AFTER[k]} for k in BEFORE},
            "spec_change_note": "RRL_STOCK_UNIT_CORE spec gains restore_inventory_loss; its dependents recompile (apply runs compile_schema; first call after is cold, see C-0165)",
            "unchanged_dependency_sha256": UNCHANGED, "before_sha256": BEFORE, "after_sha256": AFTER,
            "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}
(D / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"before": BEFORE, "after": AFTER}, indent=1))
