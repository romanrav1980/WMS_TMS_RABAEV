from pathlib import Path
import ast,json
p=Path("scripts/ni061_marked_source_case.py");s=p.read_text(encoding="utf-8")
s=s.replace("225","291")
s=s.replace("values(:a,1,1,'admin')","values(:a,1,0,'admin')")
start=s.index(' for system,profile in[(');end=s.index(' meta("insert into RRL_STOCK_POLICY_GUARD',start);s=s[:start]+s[end:]
start=s.index(' units=[');end=s.index('\n q.execute("select min(CUSTOMER_ID)',start);s=s[:start]+' units=[]'+s[end:]
s=s.replace('assert q.fetchone()==(3,3)','assert q.fetchone()==(0,None)')
s=s.replace('assert planned["unit_capture_required"]and planned["physical_unit_count"]==3','assert not planned["unit_capture_required"]and planned["physical_unit_count"]==0')
s=s.replace('  print("PASS291 marked original FULLPAL birth3/codes6/native pick-bind/current unique QC/native load/depart/immutable exact unit fingerprint interwarehouse plan/replay/source uniqueness/no plan goods effect/no governmentACK/protected13520/20",tag,article,lot,ware,target,shipop,plan_body["operation_id"],trip,target_trip,inbound,outbound,flush=True)','''  context={"tag":tag,"article":article,"lot":lot,"warehouse":ware,"target_warehouse":target,"source_load":shipop,"plan_operation_id":plan_body["operation_id"],"source_trip":trip,"target_trip":target_trip,"inbound":inbound,"outbound":outbound,"barcode":gtin,"source_quantity":"3"}
  Path("tmp/context291.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
  print("SOURCE291 original ordinaryFULLPAL born3/picked3/singleload/depart P0 ->frozeninterwareplan3, no physicalunit registry/protected20-20")''')
s=s.replace('cfg=get_settings();tag=uuid4().hex[:10];','''cfg=get_settings()
if Path("tmp/context291.json").exists():raise SystemExit("SOURCE291 already retained; use case291_partial.py without recreating")
tag=uuid4().hex[:10];''')
# Inventory ordinary birth omits marking capture; retain the already existing source workflow.
tree=ast.parse(s)
class OrdinaryCapture(ast.NodeTransformer):
 def visit_Dict(self,node):
  self.generic_visit(node);pairs=[(k,v)for k,v in zip(node.keys,node.values)if not isinstance(k,ast.Constant)or k.value!="capture"]
  node.keys=[k for k,v in pairs];node.values=[v for k,v in pairs];return node
tree=OrdinaryCapture().visit(tree);ast.fix_missing_locations(tree);s=ast.unparse(tree)+"\n"
# Persist IDs before physical birth for safe manual continuation if an intermediate step fails.
needle="        ctx = api("
position=s.index(needle)
s=s[:position]+'''        Path("tmp/source291_progress.json").write_text(json.dumps({"tag":tag,"article":article,"lot":lot,"warehouse":ware,"src":src,"dst":dst,"shipcell":shipcell,"task":task,"st":st,"st_uid":st_uid,"order":order,"wave":wave,"revision":revision,"trip":trip,"vehicle":vehicle,"dock":dock,"barcode":gtin},indent=2),encoding="utf-8")
'''+s[position:]
print(json.dumps({"scripts/source291_ordinary_case.py":s},ensure_ascii=True))
