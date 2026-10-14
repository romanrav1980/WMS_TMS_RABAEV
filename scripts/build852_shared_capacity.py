from pathlib import Path
import json,hashlib
source=Path("tmp/851_capacity_body.sql").read_text(encoding="utf-8")
start=source.index("  for r in(select rt.ARTICUL")
end=source.index("  for r in(select p.ARTICUL",start)
# The next loop's n:=0 is preserved in the replacement.
new="""  for r in(
   select *from(
    select rt.ARTICUL,rt.QTY,rt.SOURCE_RESERVATION_ID,rt.PALLET_UID,rt.SOURCE_CELL_CODE,
     rt.REPLENISHMENT_QTY_MODE,rem.REMAIN WHOLE_SOURCE_QTY,rt.PICK_WAVE_REPLENISH_TASK_ID,
     nvl((select sum(m.BASE_QTY)from RRL_WAREHOUSE_TASK t join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=t.TASK_ID
      where t.TASK_SOURCE='WAVE'and t.TASK_TYPE='REPLENISHMENT'and t.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID),0)ARRIVED,
     row_number()over(partition by rt.REPLENISHMENT_QTY_MODE,
      case when rt.REPLENISHMENT_QTY_MODE='FULL_PALLET'then rt.PALLET_UID else to_char(rt.PICK_WAVE_REPLENISH_TASK_ID)end,
      rt.SOURCE_CELL_CODE order by rt.PICK_WAVE_REPLENISH_TASK_ID)PHYSICAL_RANK
    from RRL_PICK_WAVE_REPLENISH_TASK rt
    left join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=rt.SOURCE_RESERVATION_ID
    left join RRL_REMAINS rem on rem.UID_POLETA=rt.PALLET_UID and rem.CELL=rt.SOURCE_CELL_CODE
    where rt.TARGET_CELL_CODE=p_cell and rt.SOURCE_RESERVATION_ID is not null
     and rt.STATUS not in('DONE','CANCELLED','FAILED')
     and(p_exclude_repl is null or rt.PICK_WAVE_REPLENISH_TASK_ID!=p_exclude_repl)
     and(nvl(rt.REPLENISHMENT_QTY_MODE,'BASE')!='FULL_PALLET'or(
      sr.UID_PALLET=rt.PALLET_UID and sr.CELL=rt.SOURCE_CELL_CODE
      and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')and sr.RESERVATION_KIND='HARD'
      and sr.BASE_QTY>0 and rem.REMAIN>0 and sr.ARTICUL=rt.ARTICUL
      and not exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK excluded
       where excluded.PICK_WAVE_REPLENISH_TASK_ID=p_exclude_repl
        and excluded.REPLENISHMENT_QTY_MODE='FULL_PALLET'
        and excluded.PALLET_UID=rt.PALLET_UID and excluded.SOURCE_CELL_CODE=rt.SOURCE_CELL_CODE
        and excluded.TARGET_CELL_CODE=rt.TARGET_CELL_CODE)))
   )where PHYSICAL_RANK=1 order by PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20881,'PICK_CAPACITY_OPEN_ARRIVAL_BOUND');end if;
   if r.REPLENISHMENT_QTY_MODE='FULL_PALLET'then
    if RRL_WEIGHT_BOX_CAPACITY.enabled(r.ARTICUL)=1 then
     v_arriving:=v_arriving+RRL_WEIGHT_BOX_CAPACITY.physical_volume(r.PALLET_UID,r.SOURCE_CELL_CODE,r.WHOLE_SOURCE_QTY);
    else v_arriving:=v_arriving+r.WHOLE_SOURCE_QTY*volume_for(r.ARTICUL);end if;
   elsif RRL_WEIGHT_BOX_CAPACITY.enabled(r.ARTICUL)=1 then
    v_arriving:=v_arriving+RRL_WEIGHT_BOX_CAPACITY.reservation_volume(r.SOURCE_RESERVATION_ID,greatest(0,r.QTY-r.ARRIVED));
   else v_arriving:=v_arriving+greatest(0,r.QTY-r.ARRIVED)*volume_for(r.ARTICUL);end if;
  end loop;
  n:=0;
"""
value=source[:start]+new+source[end:]
d="db/migrations/2026-10-13_ni032_shared_capacity/"
mid="2026-10-13-852-ni032-shared-capacity"
ledger=f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'One physical full-pallet incoming capacity claim for shared wave owners; BASE retained separately',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files={d+"000_before_capacity.sql":source,d+"001_capacity.sql":value,d+"002_ledger.sql":ledger,d+"apply.sql":"@@001_capacity.sql\n@@002_ledger.sql\n",d+"rollback.sql":f"@@000_before_capacity.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';\n/\n",d+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_REPL_CAPACITY';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_REPL_CAPACITY';\n",d+"checkpoint.json":json.dumps({"migration_id":mid,"state":"PREPARED","before_sha256":hashlib.sha256(source.encode()).hexdigest(),"after_sha256":hashlib.sha256(value.encode()).hexdigest(),"target":"RABAEV/orcl"},indent=2)}
page="""# NI03.2: физическая вместимость общей подачи

Migration ID:2026-10-13-852-ni032-shared-capacity. Подготовлено до применения; live source851 captured/SHA/paired rollback. Владелец inventory, authoritative RRL_STOCK_REPL_CAPACITY; без изменения запаса/публичной сигнатуры.

Partial shared-owner850 выявил, что несколько logical replenishment rows одной целой паллеты одновременно занимают projected volume. Вместимость должна считать одну физическую FULL_PALLET на UID/source-cell/target-cell. BASE задачи остаются отдельными. Уже прибывшая source reservation не считается новым incoming; её физический запас учитывается в occupied.

При проверке прибытия исключается весь matching FULL cohort указанного RT, не только один logical row. Whole quantity берётся из текущего физического REMAIN; для weighted FULL используется прежний physical_volume, для BASE сохранён reservation_volume. Требования совпадающего source UID/cell/active HARD и существующая native shared-owner admission сохраняются; разных target здесь нет, reader задан одним p_cell. Нет освобождения склада, нового stock writer или решения государственного сервиса.

Проверить compile и свежий partial shared-owner: first whole arrival2+4, remaining6+4, requeue old unissued owner, one second physical12/shared third2, true capacity refusal and replay. Weighted FULL branch independent evidence remains open. Все собственные failed850 данные очищены finally; failed attempt не passed. [SQL](../../db/migrations/2026-10-13_ni032_shared_capacity/apply.sql).
"""
files["wiki/database/nicora_ni032_shared_capacity_20261013.md"]=page
p=Path("wiki/index.md")
files[str(p)]="- [NI03.2 shared capacity852](database/nicora_ni032_shared_capacity_20261013.md): prepared one physical incoming perFULL cohort; partial shared849 requeue/native actual pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 prepared852: captured live capacity851; FULL physical cohort dedup/current location/exclude matching cohort, BASE unchanged/weighted existing physical_volume; SHA/paired rollback/wiki before apply. Partial shared849 requeue implemented, fresh850 still blocked by projected duplicate incoming, owncleanup; not passed.\n"
print(json.dumps(files,ensure_ascii=True))
