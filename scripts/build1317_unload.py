import json
from pathlib import Path
d=Path("db/migrations/2026-10-14_ni053_stock_pallet_unload")
s=(d/"000_before_body.sql").read_text(encoding="utf-8")
old="""  if method_value='PALLET'and(root_node.get_string('kind')!='CONTAINER'or root_node.get_string('type')!='PALLET')
   then raise_application_error(-20886,'UNLOAD_PALLET_SOURCE_REQUIRED');end if;"""
new="""  if method_value='PALLET' then
   if nvl(root_node.get_string('kind'),'~')='CONTAINER'and nvl(root_node.get_string('type'),'~')='PALLET' then null;
   elsif nvl(root_node.get_string('kind'),'~')='STOCK' then
    -- Frozen physical loading proof, never infer pallet type from current SKU/store settings.
    select count(*)into n from RRL_TT_LOAD_FLOOR_FACT f
     join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
     join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
     where f.LOAD_OPERATION_ID=load_op and f.TYPE_ORIGIN='ROOT_STOCK_TYPE'
      and l.ROOT_UID=p_domain.get_string('root')and l.STATUS='DEPARTED'and o.STATE='APPLIED'
      and json_value(f.CONFIRMATION_JSON,'$.root')=l.ROOT_UID
      and json_value(f.CONFIRMATION_JSON,'$.type_origin')='ROOT_STOCK_TYPE'
      and json_value(f.CONFIRMATION_JSON,'$.pallet_type_id' returning number)=f.PALLET_TYPE_ID;
    if n!=1 then raise_application_error(-20886,'UNLOAD_PALLET_LOADING_PROOF_REQUIRED');end if;
   else raise_application_error(-20886,'UNLOAD_PALLET_SOURCE_REQUIRED');end if;
  end if;"""
assert s.count(old)==1
s=s.replace(old,new)
# JSON member invocation cannot be used directly in SQL, use existing load-bound start row root.
s=s.replace("l.ROOT_UID=p_domain.get_string('root')","l.ROOT_UID=s.ROOT_KEY ")
files={str(d/"001_body.sql"):s,str(d/"apply.sql"):"@@001_body.sql\n@@002_ledger.sql\n",str(d/"rollback.sql"):"@@000_before_body.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-14-1316-stock-pallet-unload';\n/\n",str(d/"verify.sql"):"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STORE_UNLOAD_CORE';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STORE_UNLOAD_CORE';\n"}
files[str(d/"002_ledger.sql")]=Path("db/migrations/2026-10-14_ni053_driver_workspace/002_ledger.sql").read_text(encoding="utf-8").replace("2026-10-14-1302-driver-workspace","2026-10-14-1316-stock-pallet-unload").replace("Authenticated driver current binding and idempotent existing transport operation facts","Store pallet unloading accepts original frozen ROOT_STOCK_TYPE loading proof")
files["wiki/database/nicora_ni053_stock_pallet_unload_20261014.md"]="""# NI05.3: выгрузка обычной WMS-паллеты

Миграция 2026-10-14-1316-stock-pallet-unload, PREPARED. На собственном рейсе33571 приёмка отказала UNLOAD_PALLET_SOURCE_REQUIRED: старый RRL_STORE_UNLOAD_CORE принимал метод PALLET только для CONTAINER/PALLET, хотя обычный ROOT_STOCK_TYPE уже подтверждён при физической погрузке.

Используем существующий неизменяемый RRL_TT_LOAD_FLOOR_FACT именно исходной погрузки: ROOT_STOCK_TYPE, тот же root, согласованный pallet_type_id, DEPARTED/APPLIED. Текущие настройки SKU/адресата не заменяют отгрузочный факт. Отсутствие доказательства отклоняется. Приёмка остаётся в прежнем ядре, остатки повторно не списываются. HU и ручная выгрузка сохраняют свои правила; способ ROLL_CAGE этим изменением не расширен.

Свежий LIVE checkpoint содержит package body и INVALID=[]; rollback только кода, журнал не удаляется. Actual/UI/SQL evidence после применения.
"""
files["wiki/index.md"]=Path("wiki/index.md").read_text(encoding="utf-8")+"\n- [Выгрузка обычной паллеты1316](database/nicora_ni053_stock_pallet_unload_20261014.md): исходный frozen loading proof для ROOT_STOCK_TYPE; prepared.\n"
files["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n- 2026-10-14:1316 prepared NI05.3 stock-pallet unloading, own B03 refusal reproduced; existing immutable floor proof reused, checkpoint/rollback saved.\n"
print(json.dumps(files,ensure_ascii=True))
