from pathlib import Path
import json,hashlib
folder="db/migrations/2026-10-13_ni072_shared_wait_target/"
files={}
def read(n,k="package_body"):return Path("tmp/1081_"+n+"_"+k+".sql").read_text(encoding="utf-8")
spec=read("rrl_st_defer_hu_wait","package")
spec=spec.replace("package RRL_ST_DEFER_PLACE_READ)as","package RRL_ST_DEFER_PLACE_READ,package RRL_STOCK_HU_CMD)as")
spec=spec.replace(" function snapshot_root("," function shared_wait_target(p_request clob,p_task number,p_target varchar2,p_ware number)return boolean;\n function snapshot_root(",1)
body=read("rrl_st_defer_hu_wait")
pos=body.index(" procedure request_plan(")
addition=""" function shared_wait_target(p_request clob,p_task number,p_target varchar2,p_ware number)return boolean is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');value json_object_t;
  v_decision varchar2(100):=m.get_string('defer_decision_operation_id');v_count number;v_plan varchar2(100);
 begin
  if p_task is not null then
   select count(*),min(PLAN_OPERATION_ID)into v_count,v_plan from RRL_ST_DEFER_WAIT_PLAN where TASK_ID=p_task and BASE_UOM='HU';
   if v_count=0 then return false;end if;
   select DECISION_OPERATION_ID into v_decision from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=v_plan;
  elsif v_decision is null then return false;
  end if;
  describe(v_decision,d.get_string('actor'),p_task,value,m.get_string('defer_requested_root'));
  if value.get_string('root')!=d.get_object('source').get_string('uid')
    or value.get_string('target_cell')!=p_target or value.get_number('warehouse')!=p_ware
    then raise_application_error(-20886,'DEFER_SHARED_WAIT_ROOT_TARGET_REQUIRED');end if;
  return true;
 end;

"""
body=body[:pos]+addition+body[pos:]
hu=read("rrl_stock_hu_cmd")
needle="v_slot_json clob;v_claim number;"
assert needle in hu
hu=hu.replace(needle,needle+"v_wait_shared boolean:=false;",1)
needle="   select count(*) into v_count from RRL_REMAINS where CELL=v_target"
assert needle in hu
hu=hu.replace(needle,"   v_wait_shared:=RRL_ST_DEFER_HU_WAIT.shared_wait_target(p_request,v_ignore_task,v_target,v_target_ware);\n"+needle,1)
for reason in("HU_MOVE_EMPTY_TARGET_REQUIRED","HU_MOVE_TARGET_HAS_CONTAINER","HU_MOVE_TARGET_HAS_OPEN_ARRIVAL"):
 old="if v_count>0 and v_slot is null then raise_application_error(-20886,'"+reason+"');end if;"
 assert old in hu,reason
 hu=hu.replace(old,old.replace(" then "," and not v_wait_shared then "),1)
place=read("rrl_st_defer_place_read")
place=place.replace("v_plan_source clob;","v_plan_source clob;v_saved json_object_t;")
old="     if dbms_lob.compare(v_plan_source,source.to_clob)!=0"
assert old in place
place=place.replace(old,"     v_saved:=json_object_t.parse(v_plan_source);v_saved.remove('cohort_manifest');v_plan_source:=v_saved.to_clob;\n"+old,1)
files[folder+"001_wait_spec.sql"]=spec
files[folder+"002_wait_body.sql"]=body
files[folder+"003_hu_command.sql"]=hu
files[folder+"004_place_display.sql"]=place
compile_sql=Path("db/migrations/2026-10-13_ni072_place_selection/007_compile.sql").read_text(encoding="utf-8")
files[folder+"005_compile.sql"]=compile_sql
files[folder+"apply.sql"]="".join("@@"+n+"\n"for n in("001_wait_spec.sql","002_wait_body.sql","003_hu_command.sql","004_place_display.sql","005_compile.sql"))
for n,k in(("rrl_st_defer_hu_wait","package"),("rrl_st_defer_hu_wait","package_body"),("rrl_stock_hu_cmd","package_body"),("rrl_st_defer_place_read","package_body")):
 files[folder+"000_before_"+n+"_"+k+".sql"]=read(n,k)
files[folder+"rollback.sql"]="".join("@@000_before_"+n+"_"+k+".sql\n"for n,k in(("rrl_st_defer_hu_wait","package"),("rrl_st_defer_hu_wait","package_body"),("rrl_stock_hu_cmd","package_body"),("rrl_st_defer_place_read","package_body")))+"@@005_compile.sql\n"
files[folder+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-013-ni072-shared-wait-target","state":"PREPARED","retained_tasks":[1154,1155],"rollback":"Paired source restoration only, untested; no stock/history deletion.","files":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in files.items()}},indent=2)+"\n"
wiki="wiki/database/nicora_ni072_shared_wait_target_20261013.md"
files[wiki]="# NI07.2 — несколько мест в зоне ожидания\n\n1082 PREPARED. Миграция 2026-10-13-013-ni072-shared-wait-target. При выполнении уже созданного HU1154 и CASE1155 старое правило HU запрещает другой открытый приход в общую ячейку: ORA20886/HU_MOVE_TARGET_HAS_OPEN_ARRIVAL. Отказ не изменил P20/H20; планы сохранены.\n\nИсполнитель остаётся RRL_STOCK_POSTING_API → RRL_STOCK_HU_CMD. Ослабление требования пустоты разрешено только после describe текущего решения ожидания: права, склад, рейс, конфигурация, полный состав собственного Root, target и отсутствие физических slots проверяются прежним обработчиком. Generic HU сохраняет эксклюзивный target. Конкуренция сериализуется существующим CELL fence/anchor; target_json и ограничения назначения сохраняются. Это зона ожидания, а не адрес одиночного хранения. Завершение повторно проверяет источник/решение под объявленными блокировками.\n\nОтдельно display исключает cohort_manifest из сравнения физического источника CASE; сам manifest продолжает проверяться при проведении. Парные свежие исходники1081, checksum, rollback без изменения данных; live compilation и выполнение двух мест ожидают.\n"
files["wiki/index.md"]="- [Shared waiting target1082](database/nicora_ni072_shared_wait_target_20261013.md): guarded shared zone for current defer HU; retained1154/1155 before resume.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
files["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n- 2026-10-13 1082: PREPARED shared WAIT target correction after actual sibling arrival rejection; no stock changed, original plans retained, generic exclusivity preserved.\n"
print(json.dumps(files,ensure_ascii=True))
