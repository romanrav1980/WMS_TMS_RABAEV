from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni062_marked_placement")
s=(f/"000_before_rrl_stock_store_return_put.sql").read_text(encoding="utf-8").replace(" procedure compile_command"," procedure assert_scope(p_receipt varchar2,p_actor varchar2);\n procedure compile_command",1)
i=s.index(" procedure describe_current")
scope=""" procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_STORE_RETURN_RECEIPT r join RUSERS u on u.ID=p_actor where r.OPERATION_ID=p_receipt and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(p_actor,'warehouse_return_place')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_PLACEMENT_ACTOR_REQUIRED');end if;
 end;
"""
s=s[:i]+scope+s[i:];out[str(f/"001_placement.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8");needle="  if g_kind='STORE_RETURN_RECEIVE'"
s=s.replace(needle,"  if g_kind='STORE_RETURN_PUTAWAY_PLAN'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_RETURN_PUT.assert_scope(doc.get_object('source').get_string('receipt_operation_id'),p_actor);end;end if;\n"+needle);out[str(f/"002_root.sql")]=s
out[str(f/"003_recompile.sql")]="".join("alter package "+p+" compile body;\n/\n"for p in["RRL_STOCK_TASK_PLAN","RRL_STOCK_TASK_CORE","RRL_STOCK_TASK_DOMAIN","RRL_STOCK_POSTING_API"])
out[str(f/"rollback.sql")]="@@000_before_rrl_stock_posting_api.sql\n@@000_before_rrl_stock_store_return_put.sql\n@@003_recompile.sql\n"
out["wiki/database/nicora_ni062_marked_placement_design_20261011.md"]="# NI06.2: прежнее размещение маркированного возврата\n235 reuses original return putaway/task/transfer/unit owners; no new stock mover or marked task. Current placement actor/WARE before cached plan/after wait. Actual234 blocked receipt moves same unit/current UID into blocked disposal target, birth/code identity retained; eligibility remains blocked by cell.\n"
print(json.dumps(out,ensure_ascii=True))
