from pathlib import Path
import json,re,hashlib
source=Path("tmp/833_wave_body.sql").read_text(encoding="utf-8")
start=source.index("  if v_left>0 then")
end=source.index("  v_release_left:=v_taken;",start)
new="""  -- Compute releases without changing global batch accounting until admission succeeds.
  v_release_left:=v_taken;
  for i in 0..old_a.get_size-1 loop
   x:=treat(old_a.get(i)as json_object_t);
   v_release:=least(v_release_left,RRL_STOCK_MATH.quantity(x.get_string('quantity')));
   v_release_left:=v_release_left-v_release;
   x.put('release_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_release));old_a.put(i,x,true);
  end loop;
  if v_left>0 then
   if v_taken<=0 or p_mode!='FULL_PALLET' then p_decision.put('reason','PARTIAL_TARGET_WHOLE_SOURCE_REQUIRED');return;end if;
   -- Retain every untouched own binding. Issue only the first whole source;
   -- the existing REPL_CONTINUATION calculates further own demand after its receipt.
   v_count:=0;
   for i in 0..old_a.get_size-1 loop
    x:=treat(old_a.get(i)as json_object_t);
    if RRL_STOCK_MATH.quantity(x.get_string('quantity'))>RRL_STOCK_MATH.quantity(x.get_string('release_quantity'))then
     v_count:=v_count+1;
     if v_source is null then v_source:=json_object_t.parse(x.to_clob);end if;
    end if;
   end loop;
   if v_source is null then raise_application_error(-20890,'TARGET_SUPPLY_RETAINED_OWNER_REQUIRED');end if;
   p_decision.put('remaining_source_binding_count',v_count);
   v_source_uid:=v_source.get_string('uid');v_source_cell:=v_source.get_string('cell');
   -- Multiple retained bindings on the same selected physical stock require a
   -- separate exact-owner arrival plan; do not infer their incoming quantity.
   v_count:=0;
   for i in 0..old_a.get_size-1 loop
    x:=treat(old_a.get(i)as json_object_t);
    if x.get_string('uid')=v_source_uid and x.get_string('cell')=v_source_cell
     and RRL_STOCK_MATH.quantity(x.get_string('quantity'))>RRL_STOCK_MATH.quantity(x.get_string('release_quantity'))then v_count:=v_count+1;end if;
   end loop;
   if v_count!=1 then p_decision.put('reason','PARTIAL_TARGET_DISTINCT_RETAINED_SOURCE_REQUIRED');return;end if;
   select REMAIN,STOCK_VERSION into v_source_p,v_source_ver from RRL_REMAINS where UID_POLETA=v_source_uid and CELL=v_source_cell;
   p_decision.put('whole_source_quantity',v_source_p);
   if p_capacity is not null and v_source_p>p_capacity then p_decision.put('reason','WHOLE_SOURCE_EXCEEDS_REMAINING_TARGET_CAPACITY');return;end if;
   v_release:=RRL_STOCK_MATH.quantity(v_source.get_string('release_quantity'));
   v_source.put('remaining_owner_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(RRL_STOCK_MATH.quantity(v_source.get_string('quantity'))-v_release));
   v_source.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_source_p));
   v_source.put('remaining_total_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_left));
   v_source.put('reservation_version',v_source.get_number('version')+case when v_release>0 then 1 else 0 end);
   v_key:=RRL_STOCK_LOCK_API.resource_key('STOCK',v_source_uid,v_source_cell);
   v_count:=0;
   for i in 0..old_a.get_size-1 loop
    x:=treat(old_a.get(i)as json_object_t);
    if x.get_string('uid')=v_source_uid and x.get_string('cell')=v_source_cell
     and RRL_STOCK_MATH.quantity(x.get_string('release_quantity'))>0 then v_count:=v_count+1;end if;
   end loop;
   v_source.put('stock_version',v_source_ver+nvl(p_changes.get_number(v_key),0)+v_count);
  end if;

"""
value=source[:start]+new+source[end:]
# Version accounting must match actual positive releases; untouched reservations retain their version.
old="p_changes.put(v_key,nvl(p_changes.get_number(v_key),0)+1);"
pos=value.index(old,value.index("  v_release_left:=v_taken;",start+len(new)))
value=value[:pos]+"if v_release>0 then "+old+"end if;"+value[pos+len(old):]
old="RRL_STOCK_UNIT_CORE.release_units(v_rid,v_release_qty,null,0);"
pos=value.index(old)
value=value[:pos]+"if v_release_qty>0 then "+value[pos:]
old="RRL_STOCK_RESERVE_CORE.release_hard(v_rid,v_release_qty,v_version,'PICK_WAVE',rt.PICK_WAVE_ID,p_actor);"
pos=value.index(old)
value=value[:pos]+old+"end if;"+value[pos+len(old):]
d="db/migrations/2026-10-13_ni032_sequential_sources/"
mid="2026-10-13-834-ni032-sequential-sources"
ledger=f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Partial target rebind retains multiple distinct own sources and reuses original sequential replenishment continuation',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files={d+"000_before_wave.sql":source,d+"001_wave.sql":value,d+"002_ledger.sql":ledger,d+"apply.sql":"@@001_wave.sql\n@@002_ledger.sql\n",d+"rollback.sql":f"@@000_before_wave.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='{mid}';\n/\n",d+"verify.sql":"select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_WAVE_CMD';\nselect LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_WAVE_CMD';\n"}
files[d+"checkpoint.json"]=json.dumps({"migration_id":mid,"before_sha256":hashlib.sha256(source.encode()).hexdigest(),"after_sha256":hashlib.sha256(value.encode()).hexdigest(),"target":"RABAEV/orcl","state":"PREPARED","new_stock_writer":False},indent=2)
page="""# NI03.2: последовательные оставшиеся источники

Migration ID: 2026-10-13-834-ni032-sequential-sources. Подготовлено до применения. Владелец inventory; authoritative rule — прежний RRL_STOCK_WAVE_CMD. Единственная транзакция запасов/резервов/outbox — RRL_STOCK_POSTING_API.

Расширяется существующая partial target replacement: target4 при собственных bindings6+6 оставляет source2+6. Первый источник подаётся целиком обычным заданием. Следующую потребность вычисляет уже установленный RRL_STOCK_REPL_CONTINUATION по HARD владельца в целевой ячейке, а не по массе всей привезённой паллеты. Новый движок/параллельные задания не создаются.

Неизменённые bindings сохраняют количество и версии; release0 не вызывается. В закрытии ресурсов остаются все старые источники и резервы, executor перепроверяет каждый original binding даже при нулевом освобождении. Допуск целой первой паллеты по вместимости прежний; следующая подача проходит тот же планировщик после подтверждённого движения. Другой владелец HARD сохраняется. Несколько оставшихся bindings на одном выбранном UID/cell требуют отдельной точной схемы поступления и отвергаются.

Сохранён текущий live source833, SHA checkpoint и paired rollback. [SQL](../../db/migrations/2026-10-13_ni032_sequential_sources/apply.sql). Проверить свежий частный dev источник: отказ вместимости, rebind2+6, сохранение второго владельца, физическое продолжение/outer rollback/replay и compile. Старые factory632/protected source773 и20/20 не запускать повторно. Полный NI03.2 не закрывается этим slice.
"""
files["wiki/database/retailcase_ni032_sequential_sources_20261013.md"]=page
p=Path("wiki/index.md");files[str(p)]="- [NI03.2 sequential sources834](database/retailcase_ni032_sequential_sources_20261013.md): prepared reuse original continuation; live apply и свежий случай ожидают.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 prepared834: captured live833 RRL_STOCK_WAVE_CMD; multiple distinct retained sources use original sequential continuation, unchanged bindings/version preserved, zero releases skipped; migration/SHA/paired rollback and wiki checkpoint before apply. Not yet APPLIED or full acceptance.\n"
print(json.dumps(files,ensure_ascii=True))
