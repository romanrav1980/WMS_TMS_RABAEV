from pathlib import Path
import json
base=Path("db/migrations/2026-10-08_stock_posting_core");d=Path("db/migrations/2026-10-10_ni081_attendance_replace");out={}
source="../2026-10-10_ni081_workload_config/002_api.sql"
text=(base/source).read_text(encoding="utf-8")
needle=" procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_body clob,p_result out clob)is"
assert text.count(needle)==1
new=''' procedure replace_attendance(p_ware number,b json_object_t,r in out json_object_t)is
  v_old varchar2(100):=b.get_string('plan_operation_id');
  v_new_start timestamp with time zone;v_ware number;
 begin
  if v_old is null or length(b.get_string('reason'))<8 then
   raise_application_error(-20886,'WORKLOAD_REPLACEMENT_SOURCE_REASON_REQUIRED');end if;
  select WARE_ID into v_ware from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID=v_old for update;
  if v_ware!=p_ware then raise_application_error(-20882,'WORKLOAD_REPLACEMENT_SOURCE_WARE_FORBIDDEN');end if;
  v_new_start:=to_timestamp_tz(b.get_string('start_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  if v_new_start<=systimestamp then raise_application_error(-20886,'WORKLOAD_REPLACEMENT_FUTURE_INTERVAL_REQUIRED');end if;
  cancel_attendance(p_ware,b,r);
  store_attendance(p_ware,b,r);
  r.remove('cancelled');r.put('replaced_plan_operation_id',v_old);
  r.put('actual_presence_created',false);r.put('task_assignments_changed',false);
 end;
'''
text=text.replace(needle,new+needle)
text=text.replace("entered boolean:=false;","entered boolean:=false;v_saved boolean:=false;")
text=text.replace("('NORM','ATTENDANCE','CANCEL_ATTENDANCE')","('NORM','ATTENDANCE','CANCEL_ATTENDANCE','REPLACE_ATTENDANCE')")
needle="  RRL_STOCK_METADATA_TX.begin_change(p_actor,'resource_shift_edit');entered:=true;"
assert text.count(needle)==1
text=text.replace(needle,needle+"\n  savepoint RRL_WORKLOAD150;v_saved:=true;scoped_actor(ware,p_actor);")
needle="elsif p_action='ATTENDANCE'then store_attendance(ware,b,result);else"
assert text.count(needle)==1
text=text.replace(needle,"elsif p_action='ATTENDANCE'then store_attendance(ware,b,result);elsif p_action='REPLACE_ATTENDANCE'then replace_attendance(ware,b,result);else")
needle=" exception when others then g_operation:=null;g_tx:=null;if entered"
assert text.count(needle)==1
text=text.replace(needle," exception when others then if v_saved then rollback to RRL_WORKLOAD150;end if;g_operation:=null;g_tx:=null;if entered")
out[str(d/"001_api.sql")]=text
out[str(d/"apply.sql")]="@@001_api.sql\nalter trigger RRL_WORKLOAD_OPERATION_G compile;\nalter trigger RRL_WORKLOAD_NORM_G compile;\nalter trigger RRL_WORKLOAD_ATTEND_G compile;\nalter trigger RRL_WORKLOAD_CANCEL_G compile;\n"
manifest=json.loads((base/"current_runtime_manifest.json").read_text(encoding="utf-8"))
assert source in manifest["components"]
manifest["components"]=["../2026-10-10_ni081_attendance_replace/001_api.sql"if x==source else x for x in manifest["components"]]
out[str(base/"current_runtime_manifest.json")]=json.dumps(manifest,indent=2)+"\n"
p=Path("api/wms_api_server/app/modules/resources/api/workload_config_routes.py");text=p.read_text(encoding="utf-8")
needle="class CancelInput(CommandInput):"
text=text.replace(needle,'''class ReplaceAttendanceInput(AttendanceInput):
    plan_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    reason: str=Field(strict=True,min_length=8,max_length=500)

'''+needle)
needle='@router.post("/attendance/cancel")'
text=text.replace(needle,'''@router.post("/attendance/replace")
def replace_attendance(request: ReplaceAttendanceInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"REPLACE_ATTENDANCE",user,service)

'''+needle)
out[str(p)]=text
p=Path("api/wms_api_server/app/modules/resources/infrastructure/workload_config.py");text=p.read_text(encoding="utf-8")
needle="FINISH_AT,a.REASON"
assert text.count(needle)==1
text=text.replace(needle,needle+",\n                json_value(o.RESULT_JSON,'$.replaced_plan_operation_id')REPLACED_PLAN_OPERATION_ID")
needle="from RRL_WORKLOAD_ATTENDANCE a where"
assert text.count(needle)==1
text=text.replace(needle,"from RRL_WORKLOAD_ATTENDANCE a join RRL_WORKLOAD_OPERATION o on o.OPERATION_ID=a.PLAN_OPERATION_ID where")
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
