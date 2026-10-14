import ast,json
from pathlib import Path
source=Path("scripts/case519_ordinary_box_charge.py").read_text(encoding="utf-8")
source=source.replace('tag=uuid4().hex[:10];','assert not Path("tmp/context565.json").exists(),"One-time physical fixture; resume retained source"\ntag=uuid4().hex[:10];',1)
source=source.replace('state=loading.status(trip);','state=loading.status(trip,"admin");')
a='  op="TT.DEPART:"+tag;departed=loading.depart(op,trip,"admin");'
assert source.count(a)==1
inject="""  from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
  profiles=VehicleProfiles(OracleGateway())
  base_profile=profiles.read(vehicle,"admin")
  profile_body={"operation_id":"VEH.PROFILE565:"+tag,"vehicle_id":vehicle,"vehicle_size_class":"DEV.PROFILE565","cargo_length_mm":3000,"cargo_width_mm":2000,"cargo_height_mm":2200,"expected_version":0,"expected_source_hash":base_profile["base_hash"],"reason":"Own565 declared dimensions for departure snapshot","evidence_reference":"DEV565:"+tag}
  profile_result=profiles.configure(profile_body,"admin")
  Path("tmp/context565.json").write_text(json.dumps({"tag":tag,"warehouse":ware,"trip":trip,"vehicle":vehicle,"box":box,"root":top,"load":shipop,"profile_request":profile_body,"profile_result":profile_result,"driver":driver,"store":"Own full-pallet ST"}),encoding="utf-8")
"""
source=source.replace(a,inject+a)
# Remove old negative legacy cases; retained original pipeline creates one isolated source.
tree=ast.parse(source)
class Trim(ast.NodeTransformer):
 def visit_Expr(self,node):
  if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='print'and node.value.args and isinstance(node.value.args[0],ast.Constant)and isinstance(node.value.args[0].value,str)and node.value.args[0].value.startswith('PASS'):return None
  return self.generic_visit(node)
 def visit_Try(self,node):
  if node.handlers and node.orelse and not node.finalbody:return None
  return self.generic_visit(node)
tree=Trim().visit(tree);ast.fix_missing_locations(tree)
source=ast.unparse(tree)+"\n"
source=source.replace("tmp/context519.json","tmp/context565_completed.json")
source+="""
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as c:
 q=c.cursor();q.execute("select SOURCE_JSON,SOURCE_STATE,PROFILE_VERSION from RRL_TT_VEHICLE_SOURCE where TT_ID=:trip",trip=trip)
 wire,state,version=q.fetchone();wire=wire if isinstance(wire,dict)else json.loads(wire.read()if hasattr(wire,"read")else wire)
 assert state=="READY"and version==1 and wire["vehicle_profile"]["profile"]["vehicle_size_class"]=="DEV.PROFILE565",wire
 q.execute("select count(*),sum(case when l.DEPARTED_AT=s.CAPTURED_AT then 1 else 0 end)from RRL_TT_HU_LOAD_FACT l join RRL_TT_VEHICLE_SOURCE s on s.TT_ID=l.TT_ID and s.DEPARTURE_OPERATION_ID=l.DEPARTURE_OPERATION_ID where s.TT_ID=:trip",trip=trip);assert q.fetchone()==(1,1)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=wire["departure_operation_id"]);assert q.fetchone()==(0,)
 ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"));ctx["source"]=wire;ctx["done"]=True;Path("tmp/context565.json").write_text(json.dumps(ctx),encoding="utf-8")
 print("PASS565 original whole-place LOAD/DEPART archives profile1, carrier/type/region and one exact departure clock, replay/no second goods effect. New own source only.")
"""
print(json.dumps({"scripts/case565_depart_profile.py":source}))
