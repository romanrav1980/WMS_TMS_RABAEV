from pathlib import Path
import json
d=Path("db/migrations/2026-10-13_ni072_waiting_tasks");out={}
def src(name,kind="package_body"):
 return (d/("000_before_"+name.lower()+"_"+kind+".sql")).read_text(encoding="utf-8")
t=src("RRL_ST_DEFER_PHYSICAL","package")
t=t.replace("accessible by(package RRL_ST_DEFER_API)","accessible by(package RRL_ST_DEFER_API,package RRL_ST_DEFER_WAIT_API,package RRL_ST_DEFER_WAIT_CORE)")
t=t.replace("p_ware number)return clob","p_ware number,p_ignore_plan varchar2 default null)return clob")
assert "p_ignore_plan" in t
out[str(d/"005_physical_spec.sql")]=t
t=src("RRL_ST_DEFER_PHYSICAL")
t=t.replace("p_ware number)return clob","p_ware number,p_ignore_plan varchar2 default null)return clob")
old="and(w.UID_PALLET=x.PICKED_PALLET_UID or w.TARGET_UID_PALLET=x.PICKED_PALLET_UID);"
new="and(w.UID_PALLET=x.PICKED_PALLET_UID or w.TARGET_UID_PALLET=x.PICKED_PALLET_UID) and(p_ignore_plan is null or not exists(select 1 from RRL_ST_DEFER_WAIT_PLAN wp where wp.TASK_ID=w.TASK_ID and wp.PLAN_OPERATION_ID=p_ignore_plan));"
assert old in t
out[str(d/"006_physical_body.sql")]=t.replace(old,new)
t=src("RRL_STOCK_TASK_PLAN")
anchor="  p_policies:=v_p.to_clob;p_resources:=v_r.to_clob;p_domain:=v_domain.to_clob;"
assert anchor in t
hook="""  if v_task.TASK_SOURCE='MANUAL'and v_task.SOURCE_DOC_TYPE='ST_DEFER'then
   RRL_STOCK_PLAN_HELPER.fence(v_p,'CONFIG','WAREHOUSE',6);
   RRL_ST_DEFER_WAIT_CORE.plan_task(v_task,v_doc.get_string('actor'),v_r,v_domain);
  end if;
"""
out[str(d/"007_task_plan.sql")]=t.replace(anchor,hook+anchor)
t=src("RRL_STOCK_TASK_CORE")
anchor="  v_target:=v_domain.get_string('target_uid');"
assert anchor in t
t=t.replace(anchor,"  if v_task.TASK_SOURCE='MANUAL'and v_task.SOURCE_DOC_TYPE='ST_DEFER'then RRL_ST_DEFER_WAIT_CORE.validate_task(v_task,p_actor,v_domain.get_object('deferred_waiting'));end if;\n"+anchor)
anchor="  else raise_application_error(-20888,'TASK_DOMAIN_HANDLER_REQUIRED');end if;"
assert anchor in t
t=t.replace(anchor,"  elsif v_task.TASK_SOURCE='MANUAL'and v_task.SOURCE_DOC_TYPE='ST_DEFER'then\n   if v_qty!=v_original or v_target!=v_pallet.UID_PALLET then raise_application_error(-20886,'DEFER_WAIT_WHOLE_PALLET_REQUIRED');end if;\n"+anchor)
out[str(d/"008_task_core.sql")]=t
t=src("RRL_STOCK_TASK_DOMAIN")
anchor="  elsif p_task.TASK_SOURCE='WAVE' then"
assert anchor in t
out[str(d/"009_task_domain.sql")]=t.replace(anchor,"  elsif p_task.TASK_SOURCE='MANUAL'and p_task.SOURCE_DOC_TYPE='ST_DEFER'then\n   RRL_ST_DEFER_WAIT_CORE.complete_task(p_task,p_qty,p_target_uid,p_actor);\n"+anchor)
p=d/"003_core.sql";t=p.read_text(encoding="utf-8")
t=t.replace("nvl(STOP,0)=0 and nvl(SOST,0)=0","CONDITION='Спланирован'and nvl(DELETED,0)=0 and nvl(PAY_ORDER_ID,0)=0")
t=t.replace("  v json_object_t;\n begin\n  describe_task","  v json_object_t;v_st varchar2(100);\n begin\n  describe_task")
t=t.replace("  for x in(select p.ID,f.FULFILLMENT_ID","  v_st:=v.get_string('st_number');\n  for x in(select p.ID,f.FULFILLMENT_ID")
t=t.replace("where p.ST_NUMBER=v.get_string('st_number'))loop","where p.ST_NUMBER=v_st)loop")
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
