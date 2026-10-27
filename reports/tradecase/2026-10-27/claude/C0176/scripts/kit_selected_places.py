"""C-0176 kit: remove SELECTED physical places (RRL_SBORKA_PALLETS rows) of one assembly from a trip through the single membership
writer. RRL_TT_ADD_PALL gains an optional third argument (member id, removal only); a new command package RRL_TT_PLACE_REMOVAL_API
with its journal RRL_TT_PLACE_REMOVAL_CMD checks rights, replay and the membership snapshot. Reads live sources READ ONLY, asserted
edits, before/after SHA, apply/verify/rollback. Nothing is applied."""
import hashlib, json, os, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

D = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-27_tt_selected_places"); D.mkdir(parents=True, exist_ok=True)
NL = "\n"
WRITER = ("RRL_TT_ADD_PALL", "FUNCTION")
DEPS = (("RRL_TT_MEMBERSHIP_CTX_API", "PACKAGE"), ("RRL_TT_MEMBERSHIP_CTX_API", "PACKAGE BODY"), ("RRL_TRANSPORT_PLAN_API", "PACKAGE BODY"),
        ("RRL_ST_DEFER_API", "PACKAGE BODY"), ("RRL_TRADE_STOCK_GUARD", "PACKAGE"), ("RRL_TT_MEMBERSHIP_WRITER_GUARD", "TRIGGER"))
sha = lambda t: hashlib.sha256(t.encode()).hexdigest().upper()
src = {}
with OracleGateway().transaction("C-0176 kit sources READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in (WRITER,) + DEPS:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        src[(name, kind)] = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
        assert src[(name, kind)], (name, kind)
    cur.execute("select count(*) from USER_OBJECTS where OBJECT_NAME in('RRL_TT_PLACE_REMOVAL_API','RRL_TT_PLACE_REMOVAL_CMD')"); assert cur.fetchone()[0] == 0


def edit(text, old, new):
    assert text.count(old) == 1, old[:90]
    return text.replace(old, new)


before = src[WRITER]
after = before
after = edit(after, "function RRL_TT_ADD_PALL(TT_ID int,ST_NUMBER1 varchar2) return varchar2 is",
             "function RRL_TT_ADD_PALL(TT_ID int,ST_NUMBER1 varchar2,p_member_id number default null) return varchar2 is\n"
             "  -- C-0176: p_member_id selects one actual place (RRL_SBORKA_PALLETS.ID) of the assembly; only removal (TT_ID=0) may select.")
after = edit(after, "    raise_application_error(-20886,'TRIP_ASSIGNMENT_INPUT_INVALID');\n  end if;",
             "    raise_application_error(-20886,'TRIP_ASSIGNMENT_INPUT_INVALID');\n  end if;\n"
             "  if p_member_id is not null and TT_ID<>0 then raise_application_error(-20886,'TRIP_MEMBER_SELECTION_REMOVAL_ONLY');end if;")
after = edit(after, "  for r in(select ID,TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=ST_NUMBER1 order by ID)loop",
             "  for r in(select ID,TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=ST_NUMBER1 and(p_member_id is null or ID=p_member_id)order by ID)loop")
after = edit(after, "  select count(*) into found from RRL_SBORKA_PALLETS where ST_NUMBER=ST_NUMBER1;",
             "  select count(*) into found from RRL_SBORKA_PALLETS where ST_NUMBER=ST_NUMBER1 and(p_member_id is null or ID=p_member_id);")

TABLE = """create table RRL_TT_PLACE_REMOVAL_CMD(
 OPERATION_ID varchar2(100) not null,
 ACTOR varchar2(50) not null,
 REQUEST_HASH varchar2(64) not null,
 TRIP_ID number not null,
 ST_NUMBER varchar2(200) not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp default systimestamp not null,
 constraint RRL_TT_PLACE_REMOVAL_CMD_PK primary key(OPERATION_ID))"""
SPEC = """package RRL_TT_PLACE_REMOVAL_API authid definer as
 -- C-0176: remove selected places of one assembly from a trip through RRL_TT_ADD_PALL(0,st,id); one transaction, journalled.
 -- The version of the assembly's membership on the trip: every place (id, trip, condition, active load) and the trip header.
 function source_hash(p_trip number,p_st varchar2) return varchar2;
 procedure remove(p_request clob,p_actor varchar2,p_result out clob);
end;"""
BODY = """package body RRL_TT_PLACE_REMOVAL_API as
 procedure fail(p_code varchar2) is begin raise_application_error(-20886,p_code);end;
 function source_hash(p_trip number,p_st varchar2) return varchar2 is s clob;n number;
 begin
  select count(*)into n from(select 1 from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and rownum<=1001);
  if n>1000 then fail('ST_ASSIGNMENT_BATCH_BOUND');end if;
  dbms_lob.createtemporary(s,true);
  for t in(select ID,nvl(CONDITION,'-')C,nvl(DELETED,0)D,nvl(PAY_ORDER_ID,0)B,nvl(TRANSPORT,'-')V from RRL_TRANSPORT_TASK where ID=p_trip)loop
   dbms_lob.append(s,'T|'||t.ID||'|'||t.C||'|'||t.D||'|'||t.B||'|'||t.V||chr(10));
  end loop;
  for m in(select sp.ID,nvl(sp.TRANSTASK_ID,0)TT,nvl(sp.CONDITION,0)C,
   (select count(*) from RRL_TT_HU_LOAD_ST ls where ls.SBORKA_PALLET_ID=sp.ID and ls.ACTIVE_FLAG=1)L
   from RRL_SBORKA_PALLETS sp where sp.ST_NUMBER=p_st order by sp.ID)loop
   dbms_lob.append(s,'M|'||m.ID||'|'||m.TT||'|'||m.C||'|'||m.L||chr(10));
  end loop;
  return rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256));
 end;
 function replay(p_op varchar2,p_actor varchar2,p_hash varchar2,p_result out clob) return boolean is old RRL_TT_PLACE_REMOVAL_CMD%rowtype;
 begin
  select*into old from RRL_TT_PLACE_REMOVAL_CMD where OPERATION_ID=p_op;
  if old.ACTOR<>p_actor or old.REQUEST_HASH<>p_hash then fail('OPERATION_CONFLICT');end if;
  p_result:=old.RESULT_JSON;return true;  -- the exact stored reply, unchanged
 exception when no_data_found then return false;
 end;
 procedure remove(p_request clob,p_actor varchar2,p_result out clob) is
  j json_object_t:=json_object_t.parse(p_request);ids json_array_t;removed json_array_t:=json_array_t();r json_object_t;
  op varchar2(100):=j.get_string('operation_id');v_trip number:=j.get_number('trip_id');v_st varchar2(200):=j.get_string('st_number');
  v_expected varchar2(64):=j.get_string('expected_source_hash');v_hash varchar2(64);v_min number;v_max number;n number;v_count number;v_id number;answer varchar2(1024);
  task_state varchar2(100);deleted_flag number;bill number;
 begin
  if op is null or v_trip is null or v_trip<=0 or v_st is null or v_expected is null or not j.has('member_ids') then fail('PLACE_REMOVAL_INPUT_INVALID');end if;
  ids:=j.get_array('member_ids');
  if ids.get_size<1 or ids.get_size>200 then fail('PLACE_REMOVAL_BATCH_BOUND');end if;
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  select count(*),count(WARE_ID),min(WARE_ID),max(WARE_ID)into n,v_count,v_min,v_max from RRL_SBORKA_PALLETS where ST_NUMBER=v_st;
  if n=0 then fail('ST_ASSIGNMENT_NOT_FOUND');end if;
  if v_count<>n then fail('ST_WAREHOUSE_REQUIRED');end if;  -- min/max ignore NULL: a place without a warehouse is refused explicitly
  if v_min<>v_max then fail('ST_WAREHOUSE_AMBIGUOUS');end if;
  -- Current rights before any stored reply, under the shared access-revision lock (as the other native commands).
  lock table RRL_ACCESS_REV in share mode wait 5;
  if RRL_ACCESS_API.allowed(p_actor,'transport_dispatch_edit','WAREHOUSE',to_char(v_min,'TM9'))<>1 then raise_application_error(-20882,'ACCESS_DENIED');end if;
  for o in(select distinct a.OWNER_ID from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID in(select f.PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT f
     where f.LEGACY_SBORKA_PALLET_ID in(select x.ID from json_table(p_request,'$.member_ids[*]' columns(ID number path '$'))x)
    union select ct.SSCC from RRL_CASE_PICK_TASK ct
     where ct.LEGACY_SBORKA_PALLET_ID in(select x.ID from json_table(p_request,'$.member_ids[*]' columns(ID number path '$'))x)))loop
   if RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,v_min,o.OWNER_ID,1)<>1 then raise_application_error(-20882,'TRADE_OWNER_ACCESS_DENIED');end if;
  end loop;
  if replay(op,p_actor,v_hash,p_result) then return;end if;
  -- The trip row first (the writer's TT -> member order); a competing command waits here and then sees the changed snapshot.
  select CONDITION,DELETED,PAY_ORDER_ID into task_state,deleted_flag,bill from RRL_TRANSPORT_TASK where ID=v_trip for update;
  -- The same operation may have been completed by a concurrent request while this one waited: the stored reply, not a new refusal.
  if replay(op,p_actor,v_hash,p_result) then return;end if;
  if nvl(deleted_flag,0)<>0 or task_state='Отгружен' or nvl(bill,0)>0 then fail('TRIP_MEMBERSHIP_CHANGE_FORBIDDEN');end if;
  if source_hash(v_trip,v_st)<>v_expected then fail('TRIP_MEMBERSHIP_SNAPSHOT_CHANGED');end if;
  select count(*)into n from(select x.ID from json_table(p_request,'$.member_ids[*]' columns(ID number path '$'))x group by x.ID having count(*)>1);
  if n>0 then fail('PLACE_REMOVAL_DUPLICATE_MEMBER');end if;
  for i in 0..ids.get_size-1 loop
   v_id:=ids.get_number(i);
   select count(*)into n from RRL_SBORKA_PALLETS where ID=v_id and ST_NUMBER=v_st and TRANSTASK_ID=v_trip;
   if n<>1 then fail('TRIP_MEMBER_NOT_ON_TRIP');end if;
   answer:=RRL_TT_ADD_PALL(0,v_st,v_id);
   removed.append(v_id);
  end loop;
  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=v_st and TRANSTASK_ID=v_trip;
  r:=json_object_t();r.put('operation_id',op);r.put('trip_id',v_trip);r.put('st_number',v_st);r.put('removed',removed);
  r.put('on_trip_after',n);r.put('stock_changed',false);r.put('source_hash_after',source_hash(v_trip,v_st));p_result:=r.to_clob;
  begin
   insert into RRL_TT_PLACE_REMOVAL_CMD(OPERATION_ID,ACTOR,REQUEST_HASH,TRIP_ID,ST_NUMBER,RESULT_JSON)values(op,p_actor,v_hash,v_trip,v_st,p_result);
  exception when dup_val_on_index then fail('OPERATION_CONFLICT');  -- the same operation on another trip: refused, the whole removal rolls back
  end;
 end;
end;"""

KW, KS, KB = "RRL_TT_ADD_PALL:FUNCTION", "RRL_TT_PLACE_REMOVAL_API:PACKAGE", "RRL_TT_PLACE_REMOVAL_API:PACKAGE BODY"
BEFORE = {KW: sha(before)}
AFTER = {KW: sha(after), KS: sha(SPEC), KB: sha(BODY)}
UNCHANGED = {f"{n}:{k}": sha(src[(n, k)]) for n, k in DEPS}
(D / "001_journal_table.sql").write_text(TABLE + ";" + NL, encoding="utf-8")
(D / "002_writer.sql").write_text("create or replace " + after + NL + "/" + NL, encoding="utf-8")
(D / "003_removal_spec.sql").write_text("create or replace " + SPEC + NL + "/" + NL, encoding="utf-8")
(D / "004_removal_body.sql").write_text("create or replace " + BODY + NL + "/" + NL, encoding="utf-8")
(D / "before_writer.sql").write_text("create or replace " + before + NL + "/" + NL, encoding="utf-8")
SAME = ("declare s clob;n number;" + NL + " procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin" + NL
        + "  dbms_lob.createtemporary(s,true);" + NL
        + "  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;" + NL
        + "  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;" + NL
        + "  dbms_lob.freetemporary(s);" + NL + " end;" + NL + "begin" + NL)
checks = lambda d, code: "".join(f" same('{k.split(':')[0]}','{k.split(':')[1]}','{v}','{code}');" + NL for k, v in d.items())
INVALID = " select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'{}');end if;" + NL
ABSENT = " select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TT_PLACE_REMOVAL_API','RRL_TT_PLACE_REMOVAL_CMD');if n<>{} then raise_application_error(-20999,'{}');end if;" + NL
END = "end;" + NL + "/" + NL
TGT = " if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;" + NL
(D / "000_preflight.sql").write_text(SAME + TGT + checks(BEFORE, "BEFORE_SOURCE_DRIFT") + checks(UNCHANGED, "DEPENDENCY_DRIFT") + ABSENT.format(0, "NEW_OBJECTS_ALREADY_EXIST")
    + INVALID.format("INVALID_BEFORE") + END, encoding="utf-8")
(D / "verify.sql").write_text(SAME + checks(AFTER, "AFTER_SOURCE_MISMATCH") + checks(UNCHANGED, "DEPENDENCY_CHANGED") + INVALID.format("INVALID_OBJECTS")
    + " select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_PLACE_REMOVAL_CMD';if n<>7 then raise_application_error(-20999,'JOURNAL_SHAPE');end if;" + NL
    + " select count(*)into n from USER_ERRORS where NAME in('RRL_TT_ADD_PALL','RRL_TT_PLACE_REMOVAL_API','RRL_TRANSPORT_PLAN_API','RRL_ST_DEFER_API');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;" + NL + END, encoding="utf-8")
(D / "rollback_verify.sql").write_text(SAME + checks(BEFORE, "BEFORE_SOURCE_NOT_RESTORED") + checks(UNCHANGED, "DEPENDENCY_CHANGED") + ABSENT.format(0, "NEW_OBJECTS_NOT_DROPPED")
    + INVALID.format("INVALID_OBJECTS") + END, encoding="utf-8")
MID, DESC = "2026-10-27-tt-selected-places", "Remove selected places of one assembly from a trip through the single membership writer"
ledger = lambda status: (f"merge into RRL_SCHEMA_MIGRATIONS d using(select '{MID}' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)" + NL
    + f"when matched then update set STATUS='{status}',APPLIED_AT=sysdate,APPLIED_BY=user" + NL
    + "when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)" + NL
    + f"values(x.MIGRATION_ID,'{DESC}',sysdate,user,'apply.sql','rollback.sql','{status}');" + NL + "commit;" + NL)
HISTORY = ("declare n number;begin" + NL
    + " -- The journal is working history of performed removals: rolling back after facts would lose it, so it is refused." + NL
    + " select count(*)into n from RRL_TT_PLACE_REMOVAL_CMD;" + NL
    + " if n<>0 then raise_application_error(-20999,'TT_PLACE_REMOVAL_HISTORY_PRESENT');end if;" + NL + "end;" + NL + "/")
(D / "apply.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "@@000_preflight.sql", "@@001_journal_table.sql", "@@002_writer.sql",
    "@@003_removal_spec.sql", "@@004_removal_body.sql", "@@verify.sql"]) + NL + ledger("APPLIED"), encoding="utf-8")
(D / "rollback.sql").write_text(NL.join(["whenever sqlerror exit failure rollback", "declare begin" + TGT + "end;", "/",
    "-- Restore only over the exact candidate sources and only while no removal was journalled (empty rollback).",
    SAME + checks(AFTER, "AFTER_SOURCE_DRIFT_REFUSED") + checks(UNCHANGED, "DEPENDENCY_DRIFT_REFUSED") + END.rstrip(NL), HISTORY,
    "drop package RRL_TT_PLACE_REMOVAL_API;", "@@before_writer.sql", "drop table RRL_TT_PLACE_REMOVAL_CMD purge;", "@@rollback_verify.sql"]) + NL + ledger("ROLLED_BACK"), encoding="utf-8")
files = sorted(f for f in os.listdir(D) if f.endswith(".sql"))
(D / "manifest.json").write_text(json.dumps({"target": "RABAEV/orcl", "migration_id": MID, "revision": "C-0176", "status": "NOT_APPLIED", "applied_by_claude": False,
    "new_objects": {KS: AFTER[KS], KB: AFTER[KB], "RRL_TT_PLACE_REMOVAL_CMD:TABLE": "7 columns, PK OPERATION_ID"},
    "shared_objects_changed": {KW: {"before_sha256": BEFORE[KW], "after_sha256": AFTER[KW]}},
    "before_sha256": BEFORE, "after_sha256": AFTER, "unchanged_dependency_sha256": UNCHANGED,
    "files_sha256": {f: hashlib.sha256((D / f).read_bytes()).hexdigest() for f in files}}, indent=1), encoding="utf-8")
print(json.dumps({"before": BEFORE, "after": AFTER}, indent=1))
