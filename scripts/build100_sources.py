from pathlib import Path
import json
base=Path("db/migrations/2026-10-08_stock_posting_core")
folder=Path("db/migrations/2026-10-10_ni063_tare_resolution")
s=(base/"407_checkpoint_before_tare_resolution.sql").read_text(encoding="utf-8-sig")
start=s.index(" procedure warehouse_actor(");end=s.index(" procedure describe_command(",start)
s=s[:start]+s[end:]
s=s.replace("warehouse_actor(p_actor,v_owner);","RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_owner);")
s=s.replace("holder_actor(p_actor,case","RRL_TARE_PARTICIPANT.holder_actor(p_actor,case")
root=(base/"406_checkpoint_before_tare_resolution.sql").read_text(encoding="utf-8-sig")
compile_hook="elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then"
assert compile_hook in root
root=root.replace(compile_hook,"elsif g_kind in('TARE_DAMAGE','TARE_WRITE_OFF') then RRL_STOCK_TARE_RESOLVE.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  "+compile_hook,1)
execute_hook="elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_CMD.execute_command"
assert execute_hook in root
root=root.replace(execute_hook,"elsif g_kind in('TARE_DAMAGE','TARE_WRITE_OFF') then RRL_STOCK_TARE_RESOLVE.execute_command(g_request,g_actor,p_result);\n  "+execute_hook,1)
guard=(Path("db/migrations/2026-10-10_ni063_tare_ledger")/"006_guards.sql").read_text(encoding="utf-8-sig")
guard=guard.replace("v_kind in('TARE_COUNT','TARE_ACCEPT')","v_kind in('TARE_COUNT','TARE_ACCEPT','TARE_DAMAGE','TARE_WRITE_OFF')")
guard+='''
create or replace trigger RRL_TARE_RESOLUTION_GUARD before insert or update or delete on RRL_TARE_RESOLUTION for each row
declare v_kind varchar2(80);
begin
 if not inserting then raise_application_error(-20863,'TARE_RESOLUTION_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 v_kind:=case when :new.RESOLUTION_KIND='DAMAGE' then 'TARE_DAMAGE' else 'TARE_WRITE_OFF' end;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_RESOLUTION',:new.OPERATION_ID,v_kind);
end;
/
'''
out={str(folder/"005_tare_command.sql"):s,str(folder/"006_root.sql"):root,str(folder/"007_guards.sql"):guard}
print(json.dumps({p:"\n".join(line for line in value.splitlines() if line.strip())+"\n" for p,value in out.items()},ensure_ascii=True))
