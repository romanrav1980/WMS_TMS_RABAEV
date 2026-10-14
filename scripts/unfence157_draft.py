import json
from pathlib import Path
p=Path("db/migrations/2026-10-10_ni081_range_proposal/002_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("  v_entered boolean:=false;v_saved boolean:=false;", "  v_saved boolean:=false;")
s=s.replace("  RRL_STOCK_CONFIG_API.begin_change(p_actor,'pick_topology_edit');v_entered:=true;\n", "")
s=s.replace(";RRL_STOCK_CONFIG_API.end_change;return;", ";return;")
s=s.replace("  savepoint RRL_RANGE157;v_saved:=true;g_tx:=dbms_transaction.local_transaction_id(true);", "  current_actor(p_actor,p_ware);\n  savepoint RRL_RANGE157;v_saved:=true;g_tx:=dbms_transaction.local_transaction_id(true);")
s=s.replace("  insert into RRL_PICK_RANGE_OPERATION(", "  begin\n  insert into RRL_PICK_RANGE_OPERATION(")
s=s.replace("   values(p_operation,p_action,p_ware,p_article,p_actor,digest,p_request,result);", """   values(p_operation,p_action,p_ware,p_article,p_actor,digest,p_request,result);
  exception when dup_val_on_index then
   select *into old from RRL_PICK_RANGE_OPERATION where OPERATION_ID=p_operation;
   if old.REQUEST_HASH!=digest or old.ACTOR!=p_actor or old.ACTION_CODE!=p_action or old.WARE_ID!=p_ware or old.ARTICLE!=p_article then
    raise_application_error(-20886,'PICK_RANGE_OPERATION_CONTENT_CONFLICT');end if;
   p_result:=old.RESULT_JSON;g_tx:=null;return;
  end;""")
s=s.replace("p_result:=result;g_tx:=null;RRL_STOCK_CONFIG_API.end_change;", "p_result:=result;g_tx:=null;")
s=s.replace("  if v_entered then RRL_STOCK_CONFIG_API.end_change;end if;raise;", "  raise;")
print(json.dumps({str(p):s}))
