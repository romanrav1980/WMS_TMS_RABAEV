from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-10_ni062_case_closure")
s=Path("db/migrations/2026-10-08_stock_posting_core/428_before117_case_work.sql").read_text(encoding="utf-8-sig")
s=re.sub(r"\n[ \t]*\n+","\n",s)
s=s.replace("when 'LOSS_CONFIRM' then 'store_loss_confirm'","when 'LOSS_CONFIRM' then 'store_loss_confirm' when 'CLOSE' then 'store_loss_confirm'")
needle="  select * into issue from RRL_STORE_DISCREPANCY_CASE where CASE_ID=p_case;"
assert needle in s;s=s.replace(needle,"  RRL_STOCK_CASE_CLOSE.actor_scope(p_case,p_actor,v_action);\n"+needle)
needle="  else\n   if issue.STATUS!='ASSIGNED'";assert needle in s;s=s.replace(needle,"  elsif v_action='CLOSE' then\n   RRL_STOCK_CASE_CLOSE.describe(p_case,p_metadata,p_actor,p_domain);\n  else\n   if issue.STATUS!='ASSIGNED'",1)
needle="  if v_action='LOSS_CONFIRM' then";assert needle in s;s=s.replace(needle,"  if v_action='CLOSE' then RRL_STOCK_CASE_CLOSE.declare_resources(v,p_operation,r);end if;\n"+needle,1)
needle="  else\n   v_line:=v.get_number('line_no');";assert needle in s;s=s.replace(needle,"  elsif v_action='CLOSE' then\n   RRL_STOCK_CASE_CLOSE.persist(v,p_actor);j.put('status','CLOSED');\n  else\n   v_line:=v.get_number('line_no');",1)
s=s.replace("set CASE_VERSION=version_after,LAST_DECISION_OPERATION=op where CASE_ID=v_case;end if;","set STATUS=case when v_action='CLOSE' then 'CLOSED'else STATUS end,CASE_VERSION=version_after,LAST_DECISION_OPERATION=op where CASE_ID=v_case;end if;")
out[str(f/"003_command.sql")]=s
s=Path("db/migrations/2026-10-10_ni062_case_work/004_guards.sql").read_text(encoding="utf-8-sig").split("create or replace trigger RRL_STORE_OBLIGATION_GUARD",1)[0]
s=s.replace("  elsif :new.STATUS!=:old.STATUS","  elsif (v_action!='CLOSE'and :new.STATUS!=:old.STATUS)")
needle="  if v_action='ASSIGN' then";s=s.replace(needle,"  if v_action='CLOSE' and(:old.STATUS!='ASSIGNED' or :new.STATUS!='CLOSED')then raise_application_error(-20863,'STORE_CASE_EXPLICIT_CLOSURE_REQUIRED');end if;\n"+needle)
out[str(f/"004_case_guard.sql")]=s
p=Path("api/wms_api_server/app/modules/delivery/api/case_work_routes.py");s=p.read_text(encoding="utf-8-sig")
s+='''\nclass Closure(CaseCommand):
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

@router.post("/{case_id}/close")
def close(case_id: str,body: Closure,user: AdminUser=Depends(require_permission("store_loss_confirm")),service: CaseWorkPort=Depends(case_work_service)) -> dict[str,Any]:
    return send(service,case_id,body,"CLOSE",user.username)
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
