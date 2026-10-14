from pathlib import Path
import json
folder=Path("db/migrations/2026-10-10_ni063_tare_ledger")
s=(folder/"002_command.sql").read_text(encoding="utf-8-sig")
s=s.replace("n number;\n trip","n number;v_offer_id varchar2(100);\n trip")
s=s.replace("select * into offer from RRL_TARE_OFFER where OPERATION_ID=s.get_string('offer_operation_id');","v_offer_id:=s.get_string('offer_operation_id');select * into offer from RRL_TARE_OFFER where OPERATION_ID=v_offer_id;")
# Verify authentication independently of legacy GLOBAL_ADMIN shortcuts.
s=s.replace("p_domain:=json_object_t();","p_domain:=json_object_t();\n select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'TARE_ACTIVE_ACTOR_REQUIRED');end if;",1)
e=(folder/"003_execute.sql").read_text(encoding="utf-8-sig")
e=e.replace("for row_record in(select BALANCE_KEY", "v_from:=hextoraw(v.get_string('from_key'));v_to:=hextoraw(v.get_string('to_key'));\n for row_record in(select BALANCE_KEY")
e=e.replace("hextoraw(v.get_string('from_key')),hextoraw(v.get_string('to_key'))","v_from,v_to")
root=Path("db/migrations/2026-10-08_stock_posting_core/401_checkpoint_before_tare.sql").read_text(encoding="utf-8-sig")
root=root.replace("elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then","elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then",1)
needle="elsif g_kind='STORE_RETURN_PUTAWAY_PLAN' then RRL_STOCK_STORE_RETURN_PUT.execute_command"
assert needle in root
root=root.replace(needle,"elsif g_kind in('TARE_COUNT','TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_CMD.execute_command(g_request,g_actor,p_result);\n  "+needle,1)
print(json.dumps({str(folder/"004_package.sql"):s+e,str(folder/"005_root.sql"):root},ensure_ascii=True))
