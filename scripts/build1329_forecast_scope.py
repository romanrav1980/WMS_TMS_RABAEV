from pathlib import Path
import json
d=Path("db/migrations/2026-10-14_ni081_forecast_norm_scope");files={}
files[str(d/"001_schema.sql")]="""declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_WORKLOAD_SCOPE_SITE';
 if n=0 then execute immediate q'[create table RRL_WORKLOAD_SCOPE_SITE(
 WARE_ID number not null,WORK_SCOPE varchar2(30)not null,SITE_CODE varchar2(50)not null,
 VERSION_NO number(19)not null,ACTIVE number(1)not null,REASON nvarchar2(500)not null,
 OPERATION_ID varchar2(100)not null unique references RRL_WORKLOAD_OPERATION(OPERATION_ID),
 CREATED_BY nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 primary key(WARE_ID,WORK_SCOPE,VERSION_NO),
 constraint RRL_WORK_SCOPE_KIND_CK check(WORK_SCOPE in('CASE_DISPATCH','FULLPAL_DISPATCH','OUTBOUND_WORKLOAD')),
 constraint RRL_WORK_SCOPE_VERSION_CK check(VERSION_NO>=1),
 constraint RRL_WORK_SCOPE_ACTIVE_CK check(ACTIVE in(0,1)))]';end if;
end;
/
"""
source=(d/"000_before_body.sql").read_text(encoding="utf-8")
addition=""" procedure store_scope(p_ware number,p_actor varchar2,b json_object_t,r in out json_object_t)is
  v_scope varchar2(30):=b.get_string('work_scope');v_site varchar2(50):=b.get_string('site_code');
  v_reason nvarchar2(500):=b.get_string('reason');v_active number;v_version number;n number;
 begin
  if v_scope is null or v_scope not in('CASE_DISPATCH','FULLPAL_DISPATCH','OUTBOUND_WORKLOAD')
   or trim(v_site)is null or length(trim(v_reason))<3 or b.get_boolean('active')is null then
   raise_application_error(-20886,'WORKLOAD_SCOPE_FIELDS_REQUIRED');end if;
  v_active:=case when b.get_boolean('active')then 1 else 0 end;
  select nvl(max(VERSION_NO),0)into v_version from RRL_WORKLOAD_SCOPE_SITE where WARE_ID=p_ware and WORK_SCOPE=v_scope;
  if nvl(b.get_number('expected_version'),-1)!=v_version then raise_application_error(-20886,'WORKLOAD_SCOPE_VERSION_CHANGED');end if;
  if v_active=1 then
   select count(*)into n from RRL_WORKLOAD_NORM x where x.WARE_ID=p_ware and x.SITE_CODE=v_site and x.ACTIVE=1
    and x.VERSION_NO=(select max(y.VERSION_NO)from RRL_WORKLOAD_NORM y where y.WARE_ID=x.WARE_ID and y.SITE_CODE=x.SITE_CODE and y.ARTICLE=x.ARTICLE and y.BASE_UOM=x.BASE_UOM);
   if n=0 then raise_application_error(-20886,'WORKLOAD_SCOPE_ACTIVE_SITE_NORM_REQUIRED');end if;
  end if;
  insert into RRL_WORKLOAD_SCOPE_SITE(WARE_ID,WORK_SCOPE,SITE_CODE,VERSION_NO,ACTIVE,REASON,OPERATION_ID,CREATED_BY)
   values(p_ware,v_scope,v_site,v_version+1,v_active,v_reason,g_operation,p_actor);
  r.put('work_scope',v_scope);r.put('site_code',v_site);r.put('version',v_version+1);r.put('active',v_active=1);
  r.put('actual_presence_created',false);r.put('task_assignments_changed',false);
 end;
"""
needle=" procedure execute_command(p_operation varchar2"
assert source.count(needle)==1
source=source.replace(needle,addition+needle)
source=source.replace("'CANCEL_ATTENDANCE','REPLACE_ATTENDANCE')","'CANCEL_ATTENDANCE','REPLACE_ATTENDANCE','FORECAST_SCOPE')")
needle="if p_action='NORM'then store_norm"
assert source.count(needle)==1
source=source.replace(needle,"if p_action='FORECAST_SCOPE'then store_scope(ware,p_actor,b,result);elsif p_action='NORM'then store_norm")
files[str(d/"002_api.sql")]=source
files[str(d/"003_guard.sql")]="""create or replace trigger RRL_WORKLOAD_SCOPE_SITE_G before insert or update or delete on RRL_WORKLOAD_SCOPE_SITE for each row
begin
 if not inserting or RRL_WORKLOAD_CONFIG_API.write_allowed(:new.OPERATION_ID)!=1 then
  raise_application_error(-20863,'WORKLOAD_SCOPE_IMMUTABLE_NATIVE_VERSION');end if;
end;
/
"""
files[str(d/"004_ledger.sql")]=Path("db/migrations/2026-10-14_ni053_driver_workspace/002_ledger.sql").read_text(encoding="utf-8").replace("2026-10-14-1302-driver-workspace","2026-10-14-1328-forecast-norm-scope").replace("Authenticated driver current binding and idempotent existing transport operation facts","Versioned explicit forecast workload scope to existing norm site")
files[str(d/"apply.sql")]="@@001_schema.sql\n@@002_api.sql\n@@003_guard.sql\n@@004_ledger.sql\n"
files[str(d/"rollback.sql")]="@@000_before_body.sql\n-- Keep configuration history and guarded table; do not delete business decisions.\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-14-1328-forecast-norm-scope';\n/\n"
files[str(d/"verify.sql")]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_WORKLOAD_CONFIG_API','RRL_WORKLOAD_SCOPE_SITE_G');\nselect OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID';\n"
files["wiki/database/nicora_ni081_forecast_norm_scope_20261014.md"]="""# NI08.1: связь прогноза с нормативом участка

Миграция2026-10-14-1328-forecast-norm-scope PREPARED. Владелец resources. Append-only RRL_WORKLOAD_SCOPE_SITE(warehouse, work_scope, version) связывает CASE_DISPATCH/FULLPAL_DISPATCH/OUTBOUND_WORKLOAD с явным SITE_CODE существующих норм RRL_WORKLOAD_NORM. Не угадываем соответствие названий, универсальную производительность или численность людей.

Запись FORECAST_SCOPE в прежнем RRL_WORKLOAD_CONFIG_API: текущий склад/право resource_shift_edit, существующая короткая metadata transaction, expected_version и исходный operation_id/hash, история и нативный guard. Replay сохраняет решение; другой payload того же ID отвергается. Обновление нормы и mapping не изменяет запас, присутствие или задания.

Read model получает mapping + актуальные нормы SKU/base_uom в том же readonly snapshot прогноза. Трудозатраты = прогноз количества / base_per_hour, Decimal; отсутствующая/неактивная норма оставляет строку без часов. Частичный итог явно отделён от полного; заблокированный прогноз не даёт рекомендацию по часам. Не вычисляем работников без плановых доступных часов и квалификации.

LIVE исходник и INVALID=[] сохранены; rollback возвращает код без удаления истории. Применение/API/UI/evidence ожидаются.
"""
p=Path("wiki/index.md");files[str(p)]="- [NI08.1 нормативы прогноза1328](database/nicora_ni081_forecast_norm_scope_20261014.md): prepared versioned scope→site, existing native config and norms, no guessed labour capacity.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1328–1329: prepared explicit forecast norm scope, LIVE workload API saved; reuse history/auth/version/native owner; no stock command.\n"
print(json.dumps(files,ensure_ascii=True))
