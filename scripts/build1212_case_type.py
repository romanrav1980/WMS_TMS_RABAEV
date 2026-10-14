import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
folder="db/migrations/2026-10-14_ni022_case_type/"
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 for name in ["RRL_STOCK_POSTING_API","RRL_TRANSPORT_PLAN_RULES"]:
  q.execute("select TYPE,TEXT from USER_SOURCE where NAME=:name order by TYPE,LINE",name=name)
  groups={}
  for typ,text in q:groups.setdefault(typ,[]).append(text)
  for typ,text in groups.items():files[folder+"000_"+name.lower()+"_"+typ.lower().replace(" ","_")+".sql"]="create or replace "+"".join(text)+"\n/\n"
original=files[folder+"000_rrl_stock_posting_api_package_body.sql"]
root=files[folder+"000_rrl_stock_posting_api_package.sql"]+original
root=root.replace("if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then declare", "if g_kind='CASE_PALLET_TYPE_CHANGE'then RRL_CASE_TASK_ACCESS.assert_scope(v_doc.get_object('source').get_number('case_task_id'),p_actor,'case_pick_execute');end if;\n  if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then declare",1)
root=root.replace("if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then RRL_STOCK_PALLET_TYPE_CMD.compile_command", "if g_kind='CASE_PALLET_TYPE_CHANGE'then RRL_STOCK_CASE_TYPE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='PALLET_FLOOR_TYPE_CONFIRM'then RRL_STOCK_PALLET_TYPE_CMD.compile_command",1)
root=root.replace("if g_kind='PALLET_FLOOR_TYPE_CONFIRM'then RRL_STOCK_PALLET_TYPE_CMD.execute_command", "if g_kind='CASE_PALLET_TYPE_CHANGE'then RRL_STOCK_CASE_TYPE_CMD.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='PALLET_FLOOR_TYPE_CONFIRM'then RRL_STOCK_PALLET_TYPE_CMD.execute_command",1)
assert root.count("RRL_STOCK_CASE_TYPE_CMD.compile_command")==1 and root.count("RRL_STOCK_CASE_TYPE_CMD.execute_command")==1
files[folder+"003_root.sql"]=root
plan=files[folder+"000_rrl_transport_plan_rules_package_body.sql"]
start=plan.index("rt.CUSTOMER_PALLET_TYPE_RULE_ID=(select")
end=plan.index(" left join RRL_PALLET_TYPE pt",start)
plan=plan[:start]+"rt.CUSTOMER_PALLET_TYPE_RULE_ID=RRL_RECIPIENT_PALLET_POLICY.rule_id(co.CUSTOMER_ID,co.CUSTOMER_STORE_MAP_ID)"+plan[end:]
files[folder+"004_plan_rule.sql"]=plan
files[folder+"apply.sql"]="@@001_policy_read.sql\n@@002_command.sql\n@@003_root.sql\n@@004_plan_rule.sql\n@@005_guard.sql\n"
files[folder+"rollback.sql"]="@@000_rrl_stock_posting_api_package.sql\n@@000_rrl_stock_posting_api_package_body.sql\n@@000_rrl_transport_plan_rules_package_body.sql\nbegin execute immediate 'drop trigger RRL_CASE_PALLET_TYPE_GUARD';end;\n/\n"
files[folder+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_RECIPIENT_PALLET_POLICY','RRL_CASE_PALLET_TYPE_READ','RRL_STOCK_CASE_TYPE_CMD','RRL_STOCK_POSTING_API','RRL_TRANSPORT_PLAN_RULES');\n"
print(json.dumps(files,ensure_ascii=True))
