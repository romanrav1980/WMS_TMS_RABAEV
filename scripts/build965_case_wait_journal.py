from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_case_wait/";p=d+"002_case_wait.sql";read=lambda p:Path(p).read_text(encoding="utf-8");body=read(p)
body=body.replace("new_version number;ff_id number;case_id number;","new_version number;ff_id number;case_id number;lots json_array_t;lot json_object_t;lot_uid varchar2(200);lot_qty number;lot_base varchar2(20);")
needle="  v_sync_id:=frozen.get_number('sync_id');"
assert body.count(needle)==1
body=body.replace(needle,"""  lots:=j.get_array('lots');
  for i in 0..lots.get_size-1 loop
   lot:=treat(lots.get(i)as json_object_t);lot_uid:=lot.get_string('uid');lot_qty:=RRL_STOCK_MATH.quantity(lot.get_string('quantity'));lot_base:=lot.get_string('base');
   insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,
    UID_PALLET,TARGET_UID_PALLET,FROM_CELL,TO_CELL,QTY,BASE_QTY,BASE_UOM,OPERATION_ID,CREATED_AT,CREATED_BY)
    values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,tid,t.TASK_SOURCE,t.TASK_TYPE,t.SOURCE_DOC_TYPE,t.SOURCE_DOC_ID,t.SOURCE_TASK_ID,
     lot_uid,lot_uid,t.FROM_CELL,t.TO_CELL,lot_qty,lot_qty,lot_base,op,systimestamp,p_actor);
  end loop;
"""+needle)
needle="  select *into p from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=tid;\n  select *into t"
body=body.replace(needle,"""  if m.has('unit_keys')then declare keys json_array_t:=m.get_array('unit_keys');begin
   if keys is not null and keys.get_size>0 then raise_application_error(-20886,'DEFER_CASE_WHOLE_CARRIER_NO_PARTIAL_UNIT_SELECTION');end if;
  end;end if;
  select *into p from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=tid;
  select *into t""")
files={p:body,d+"fix965.sql":"@@002_case_wait.sql\n@@008_compile.sql\n"}
p=d+"checkpoint.json";v=json.loads(read(p));v["correction965"]="Add existing WHT stock-move journal per actual lot/base, place FACT1 separate; reject ignored partial-unit selection. Actual964 rollback+bridge committed1110 before mistaken harness outbox table query; qty12/H12/sourcefacts/version/replay passed; follow-up retainedCASE8 pending.";v["sha256"].update({p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni072_case_wait_20261013.md";files[p]=read(p)+"\nActual964: тот же source955/CASE1129/task1110, positive native movement rollback leaves PLANNED/originalCELL/version; public bridge commit+exact replay → DONE1CASE/SYNCED/currentcellWAIT/version2/P12H12/старые pickfacts неизменны. Result outbox5096. Последний assertion harness обращался к ошибочно названной RRL_STOCK_OUTBOX, отказ00942 послеcommit; не полныйPASS. Проверяется существующая RRL_EVENT_OUTBOX.965 добавляет к прежнему WHT stock-move журналу по одной строке на фактическую партию/base и отказывает partial unit_keys; исходный Root товарный журнал уже сохранён. Второй retainedCASE1130qty8 позволит доказать текущую функцию безfactory/source rebirth.\n"
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint965:963 fixedlookup; actual964 native rollback/bridge1110DONE1CASE/P12H12/FFversion2/originalfacts/replay, outbox5096. Harnessfinal00942 wrongtable isnotPASS.965 WHT actual-lot journal/currentunitselection guard checkpoint beforeapply. Earlier963 guessedtask1107 corrected actual1110.\n"
p="wiki/index.md";files[p]="- [CASE ожидание965](database/nicora_ni072_case_wait_20261013.md): actual1110DONE1CASE/P12H12/rollback/replay; add WHT lot journal, final harness outbox corrected.\n"+read(p)
# Fix the standalone authored factory generator before future independent usage; old955source MUST NOT be rerun.
p="scripts/build955_case_wait_case.py";src=read(p).replace('source[source.index(" finally:"):]','source[source.index("\\n finally:\\n")+1:]');src=src.replace("RRL_STOCK_OUTBOX where OPERATION_ID=:op","RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(:op,'AL32UTF8'),sys.dbms_crypto.hash_sh256))");files[p]=src
print(json.dumps(files,ensure_ascii=True))
