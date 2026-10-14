from pathlib import Path
import json,hashlib
f={};root="db/migrations/2026-10-14_ni052_departure_temperature/"
spec=Path(root+"000_rrl_stock_load_thermal_spec.sql").read_text(encoding="utf-8")
body=Path(root+"000_rrl_stock_load_thermal_body.sql").read_text(encoding="utf-8")
for old,new in(("p_domain out json_object_t)","p_domain out json_object_t,p_phase varchar2 default 'MANUAL_AT_LOADING')"),("p_domain clob);","p_domain clob,p_phase varchar2 default 'MANUAL_AT_LOADING');")):
 spec=spec.replace(old,new,1)
body=body.replace("p_domain out json_object_t)is","p_domain out json_object_t,p_phase varchar2 default 'MANUAL_AT_LOADING')is",1)
body=body.replace("p_domain clob)is\n  frozen","p_domain clob,p_phase varchar2 default 'MANUAL_AT_LOADING')is\n  frozen",1)
body=body.replace("  p_domain:=null;","  p_domain:=null;\n  if p_phase is null or p_phase not in('MANUAL_AT_LOADING','MANUAL_AT_DEPARTURE')then raise_application_error(-20886,'THERMAL_PHASE_REQUIRED');end if;",1)
body=body.replace("if not ctx.has('temperature_confirmation')then raise_application_error(-20886,'LOAD_THERMAL_CURRENT_CONFIRMATION_REQUIRED');end if;","if not ctx.has('temperature_confirmation')then\n   if p_phase='MANUAL_AT_DEPARTURE'then raise_application_error(-20886,'DEPART_THERMAL_CURRENT_CONFIRMATION_REQUIRED');else raise_application_error(-20886,'LOAD_THERMAL_CURRENT_CONFIRMATION_REQUIRED');end if;\n  end if;")
body=body.replace("mode_value!='MANUAL_AT_LOADING'","mode_value!=p_phase").replace("p_domain.put('origin','MANUAL_AT_LOADING')","p_domain.put('origin',p_phase)")
body=body.replace("compile_confirmation(p_members,p_vehicle,ctx.to_clob,current_value);","compile_confirmation(p_members,p_vehicle,ctx.to_clob,current_value,p_phase);")
f[root+"001_thermal_phase.sql"]=spec+"\n"+body
s=Path(root+"000_rrl_stock_trip_depart_cmd_body.sql").read_text(encoding="utf-8")
s=s.replace("promise_wire clob;\n begin","promise_wire clob;thermal_value json_object_t;\n begin",1)
point="  v.put('incoming_promises'"
assert point in s;s=s.replace(point,"  RRL_STOCK_LOAD_THERMAL.compile_confirmation(members.to_clob,vehicle_no,d.get_object('metadata').to_clob,thermal_value,'MANUAL_AT_DEPARTURE');\n  if thermal_value is null then v.put_null('temperature_at_departure');else v.put('temperature_at_departure',thermal_value);end if;\n"+point,1)
s=s.replace("depart_instant timestamp with time zone;","depart_instant timestamp with time zone;thermal_element json_element_t;thermal_wire clob;",1)
point="  depart_instant:=systimestamp;"
assert point in s;s=s.replace(point,"  if v.has('temperature_at_departure')then thermal_element:=v.get('temperature_at_departure');if not thermal_element.is_null then thermal_wire:=thermal_element.to_clob;end if;end if;\n  RRL_STOCK_LOAD_THERMAL.assert_current(member_ids,vehicle_no,thermal_wire,'MANUAL_AT_DEPARTURE');\n"+point,1)
point="  j.put('operation_id',op);"
s=s.replace(point,"  if thermal_wire is not null then j.put('temperature_at_departure',json_object_t.parse(thermal_wire));j.put('temperature_confirmed_at',to_char(depart_instant,'YYYY-MM-DD\"T\"HH24:MI:SS.FF3TZH:TZM'));end if;\n"+point,1)
f[root+"002_depart_command.sql"]=s
f[root+"003_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1170-departure-temperature' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Separate manual current-temperature confirmation in original root departure; immutable root result/plan and same departure clock, no repeat goods consumption',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"004_compile_dependents.sql"]="""begin
 execute immediate 'alter package RRL_STOCK_HU_LOAD_CORE compile body';
 execute immediate 'alter trigger RRL_LOAD_THERMAL_FACT_GUARD compile';
 execute immediate 'alter package RRL_STOCK_POSTING_API compile body';
end;
/
"""
f[root+"apply.sql"]="@@001_thermal_phase.sql\n@@002_depart_command.sql\n@@004_compile_dependents.sql\n@@003_ledger.sql\n"
f[root+"rollback.sql"]="begin raise_application_error(-20863,'DEPART_THERMAL_FORWARD_RECOVERY_REQUIRED: keep departure protection and immutable original confirmations');end;\n/\n"
f[root+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_TRIP_DEPART_CMD','RRL_STOCK_HU_LOAD_CORE','RRL_LOAD_THERMAL_FACT_GUARD','RRL_STOCK_POSTING_API')order by NAME,TYPE,SEQUENCE;\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_TRIP_DEPART_CMD','RRL_STOCK_HU_LOAD_CORE','RRL_LOAD_THERMAL_FACT_GUARD','RRL_STOCK_POSTING_API');\n"
p=Path("api/wms_api_server/app/modules/transport/api/loading_routes.py");s=p.read_text(encoding="utf-8")
point="class DepartureRequest(BaseModel):"
s=s.replace(point,'class DepartureTemperatureConfirmation(LoadingTemperatureConfirmation):\n    origin: Literal["MANUAL_AT_DEPARTURE"]\n\n\n'+point,1)
s=s.replace('class DepartureRequest(BaseModel):\n    model_config = ConfigDict(extra="forbid")','class DepartureRequest(BaseModel):\n    model_config = ConfigDict(extra="forbid")\n    temperature_confirmation: DepartureTemperatureConfirmation | None=None',1)
point="        return service.depart(body.operation_id,task_id,user.username)"
assert point in s;s=s.replace(point,"        if body.temperature_confirmation:\n            return service.depart(body.operation_id,task_id,user.username,body.temperature_confirmation.model_dump(mode=\"json\"))\n"+point,1)
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/contracts.py");s=p.read_text(encoding="utf-8").replace('def depart(self, operation_id: str, task_id: int, actor: str)','def depart(self, operation_id: str, task_id: int, actor: str, temperature_confirmation: dict[str, Any] | None = None)');f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading.py");s=p.read_text(encoding="utf-8")
s=s.replace('def depart(self, operation_id: str, task_id: int, actor: str)','def depart(self, operation_id: str, task_id: int, actor: str, temperature_confirmation: dict[str, Any] | None = None)')
s=s.replace('return self.post("TRIP_DEPART", operation_id, {"task_id": task_id}, {}, actor)','return self.post("TRIP_DEPART", operation_id, {"task_id": task_id},\n                         {"temperature_confirmation": temperature_confirmation} if temperature_confirmation is not None else {}, actor)')
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading_thermal_read.py");s=p.read_text(encoding="utf-8")
s=s.replace("load_ids: list[str])","load_ids: list[str], trip: int)")
point='    return {"vehicle_profile":profile'
insert="""    cur.execute(\"\"\"select o.RESULT_JSON from RRL_TT_VEHICLE_SOURCE s join RRL_STOCK_OPERATION o
        on o.OPERATION_ID=s.DEPARTURE_OPERATION_ID where s.TT_ID=:trip and o.STATE='APPLIED'
        and o.COMMAND_TYPE='TRIP_DEPART'\"\"\",trip=trip)
    row=cur.fetchone()
    departed=read_oracle_json(row[0]) if row else {}
"""
assert point in s;s=s.replace(point,insert+point).replace('"load_confirmations":facts,','"load_confirmations":facts,"departure_confirmation":departed.get("temperature_at_departure"),\n            "departure_confirmed_at":departed.get("temperature_confirmed_at"),')
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading_status.py");s=p.read_text(encoding="utf-8").replace('loading_thermal_read(cur,header[1],[row["load_operation_id"]for row in loads])','loading_thermal_read(cur,header[1],[row["load_operation_id"]for row in loads],trip)');f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8")
point='<h2>Выезд</h2><button id="tripDepart">'
insert="""<h2>Выезд</h2><p id="departTempProfile">Для температурного товара подтвердите новое измерение перед выездом.</p>
<label>Температура перед выездом, °C<input id="departTempObserved" inputmode="decimal" maxlength="11"></label>
<label>Основание измерения перед выездом<input id="departTempReference" maxlength="100" autocomplete="off"></label>
<label><input id="departTempConfirm" type="checkbox">Подтверждаю измерение непосредственно перед этим выездом</label>
<button id="tripDepart">"""
assert point in s;s=s.replace(point,insert+point[len('<h2>Выезд</h2><button id="tripDepart">'):],1) if False else s.replace(point,insert,1)
s=s.replace("transport-loading.js?v=20261014-1163","transport-loading.js?v=20261014-1171")
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.js");s=p.read_text(encoding="utf-8")
point='  window.dispatchEvent(new CustomEvent("wms-physical-load-status"'
assert point in s
s=s.replace(point,'  el("departTempProfile").textContent=el("loadTempProfile").textContent+(data.temperature?.departure_confirmation?" Сохранён факт температуры выезда "+data.temperature.departure_confirmation.observed_c+" °C.":"");\n'+point,1)
point='   }else path="/api/transport/loading/"+id+"/depart";'
insert="""   }else{
    const observed=el("departTempObserved").value,reference=el("departTempReference").value;
    if(observed||reference||el("departTempConfirm").checked){
     const version=Number(el("loadTempVersion").value);
     if(!el("departTempConfirm").checked||!Number.isSafeInteger(version)||version<1||!reference.trim()||!/^-?[0-9]{1,6}(\\.[0-9]{1,3})?$/.test(observed))throw new Error("Подтвердите новое измерение перед выездом и действующий профиль машины.");
     body.temperature_confirmation={origin:"MANUAL_AT_DEPARTURE",observed_c:observed,vehicle_profile_version:version,observation_reference:reference};
    }
    path="/api/transport/loading/"+id+"/depart";
   }
"""
assert point in s;s=s.replace(point,insert)
s=s.replace('el("loadTempConfirm").checked=false;window.wmsPhysicalBoxes','el("loadTempConfirm").checked=false;el("departTempObserved").value="";el("departTempReference").value="";el("departTempConfirm").checked=false;window.wmsPhysicalBoxes',1)
f[str(p)]=s
f[root+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1170-departure-temperature","target":"RABAEV@127.0.0.1:1521/orcl","prepared_sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in f.items()if k.startswith(root)},"state":"PREPARED_NOT_APPLIED","scope":"Existing helper phase and root departure only. No new table/quantity engine. Captured immutable root plan/result stores separate manual confirmation with original departure instant."},indent=2)
p=Path("wiki/database/retailcase_ni052_departure_temperature_20261014.md");f[str(p)]="""# NI05.2 — температура перед выездом
Миграция2026-10-14-1170-departure-temperature подготовлена; ещё не применена.

Общий thermal helper получает phase=MANUAL_AT_DEPARTURE; прежний load core использует defaultMANUAL_AT_LOADING. Температурный товар требует нового подтверждения непосредственно перед выездом с текущей версией профиля. Под CFG/vehicle/TT/ST locks повторяются текущие диапазоны и профиль до смены статуса рейса. Повтор загрузочного подтверждения с origin загрузки не разрешает выезд.

Результат фиксируется в неизменяемых RESOLVED_PLAN_JSON/RESULT_JSON существующей Root операции TRIP_DEPART, вместе с исходным depart_instant, journal/outbox и RRL_TT_VEHICLE_SOURCE. Отдельного температурного журнала выезда и новой quantity транзакции нет. Товар повторно не списывается.

Оригинальный loading1160 уже установлен; отдельный тест1168/1169 загрузил собственный3EA при3.125°C: missing/20°C rejected before goods, outerrollback returned P3/H3 and nofacts, finalP0/H0/replay, protected987P20/H20. First test setup omitted mandatory PICK_CELL; resumed same retained lot/trip, не создавая заново запас.

API/интерфейс имеют отдельный ввод для выезда с разрешением transport_dispatch_close. Старые запросы без блока не приобретают null-поля в canonical metadata. Status читает сохранённое подтверждение через исходный departure operation/class-source PK в том же readonly scoped snapshot. Датчик/непрерывный контроль/придуманный TTL не заявлены. Source checkpoint/apply/verify/forward-only recovery сохранены. Native positive departure ещё ожидает.
"""
p=Path("wiki/index.md");f[str(p)]="- [Prepared1170–1171: температура выезда](database/retailcase_ni052_departure_temperature_20261014.md): separate current confirmation, original root journal/one departure clock/no repeat stock; apply pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1168–1171: one new actualprivate thermal load: missing/20°C denied, outerrollback P3H3/no physicalthermalfacts, committed3.125°C/load+thermalfact/P0H0/replay, protected987P20H20. SetupPICK_CELL omission corrected by continuation1169 ofsame lot/trip, no factoryrerun. Nextphase originaldeparture helper/root/API/UI/scoped savedresultread checkpointed; notapplied yet.\n"
print(json.dumps(f))
