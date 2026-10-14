import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.fulfillment.domain.automatic_layout import automatic_layout
from app.modules.fulfillment.api.preparation_read_routes import AutoPreparationRequest
from decimal import Decimal
from fractions import Fraction
from pydantic import ValidationError

def line(a,q="18",pack="6",norm="24",mass="4"):
 return {"articul":a,"quantity":q,"pack_quantity":pack,"pallet_norm":norm,"pack_mass":mass,"dimensions":["400","300","200"]}
limits={"max_goods_weight_kg":"16","max_goods_volume_m3":"0.096","max_pallets":100}
r=automatic_layout([line("B"),line("A")],{"A":(1,1),"B":(1,2)},limits)
assert [p["lines"]for p in r["pallets"]]==[
 [{"articul":"A","quantity":"18.000000"},{"articul":"B","quantity":"6.000000"}],
 [{"articul":"B","quantity":"12.000000"}]]
assert len(automatic_layout([line("A"),line("B")],{"A":(1,1),"B":(2,2)},limits)["pallets"])==2
assert len(automatic_layout([line("A","600","6","24")],{},limits)["pallets"])==25
r=automatic_layout([line("A","18"),line("B","24",norm="48")],{},limits)
for stats in r["pallet_statistics"]:
 assert Decimal(stats["goods_weight_kg"])<=Decimal(limits["max_goods_weight_kg"])
 assert Decimal(stats["goods_volume_m3"])<=Decimal(limits["max_goods_volume_m3"])
 assert Fraction(**stats["norm_share"])<=1
for source,lim in [
 ([line("A",norm="1")],limits),([line("A",q="7")],limits),
 ([line("A")],dict(limits,max_goods_weight_kg="3.99")),
 ([line("A")],dict(limits,max_goods_volume_m3="0.023999")),
 ([line("A",q="600")],dict(limits,max_pallets=1))]:
 try:automatic_layout(source,{},lim)
 except ValueError:pass
 else:raise AssertionError("Invalid layout accepted")
try:AutoPreparationRequest.model_validate({"operation_id":"X","source_signature":"a"*64,"limits":dict(limits,max_pallets=True)})
except ValidationError:pass
else:raise AssertionError("bool bound accepted")
print("PASS1116 exact mixed tails/group separation/full demand/floor mass+volume+norm/bounds/strict DTO")


cold={**line("A",q="6"),"temp_min_c":"2","temp_max_c":"4"}
warm={**line("B",q="6"),"temp_min_c":"15","temp_max_c":"20"}
assert len(automatic_layout([cold,warm],{},limits)["pallets"])==2
unknown=line("C",q="6")
assert len(automatic_layout([cold,unknown],{},limits)["pallets"])==2
compatible={**line("B",q="6"),"temp_min_c":"3","temp_max_c":"6"}
result=automatic_layout([cold,compatible],{},limits)
assert len(result["pallets"])==1
assert result["pallet_statistics"][0]["temp_min_c"]=="3" and result["pallet_statistics"][0]["temp_max_c"]=="4"
try:automatic_layout([{**cold,"temp_min_c":"6","temp_max_c":"2"}],{},limits)
except ValueError:pass
else:raise AssertionError("Invalid temperature range accepted")
print("PASS1147 incompatible/known-unknown separated; compatible exact3..4 mixed; invalid range rejected")
