from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_box_choice")
p=f/"002_api.sql";t=p.read_text(encoding="utf-8")
t=t.replace("  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','PHASE',null);","  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','PHASE',null);\n  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','ACTOR',null);")
a=t.index("  if sys_context('RRL_STOCK_WRITE_CTX','MODE')");b=t.index("  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','TX_ID'",a)
t=t[:a]+"""  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null or RRL_HAS_WRIGHT(p_actor,'case_pick_short_approve')!=1
   then raise_application_error(-20863,'WEIGHT_CHOICE_BUSINESS_METADATA_OWNER_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
"""+t[b:]
t=t.replace("  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));","  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));\n  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','ACTOR',p_actor);")
out[str(p)]=t
out[str(f/"005_recompile_api.sql")]=t.replace("create context RRL_WEIGHT_CHOICE_CTX using RRL_WEIGHT_BOX_CHOICE_API;\n","")
p=f/"004_guard.sql";out[str(p)]=p.read_text(encoding="utf-8").replace("sys_context('RRL_STOCK_WRITE_CTX','ACTOR')","sys_context('RRL_WEIGHT_CHOICE_CTX','ACTOR')")
print(json.dumps(out,ensure_ascii=True))
