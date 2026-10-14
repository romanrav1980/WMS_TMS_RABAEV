exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));slot=json.loads(Path("tmp/context1002.json").read_text(encoding="utf-8"))
hu=WarehouseHu(OracleGateway())
current=hu.preview(ctx["cases"][0][2],"admin")
assert current["placement"]["slot_id"]==slot["slots"][2][0]
assert current["placement"]["version_matches"] is True
assert current["placement"]["gross_weight_kg"]=="15"and current["placement"]["bounding_volume_m3"]==".75",current["placement"]
assert current["placement"]["task_status"]=="DONE"and current["placement"]["synced"] is True
assert current["placement"]["content_version"]==10
root=hu.preview(slot["root"],"admin");assert root["placement"]["slot_id"]==slot["slots"][0][0]
Path("tmp/read1008_hu_placement.json").write_text(json.dumps({"case":current,"hu":root},indent=2),encoding="utf-8")
print("PASS1008 existingHU scopedreadonly recordedslot/version/task/sync/manual15kg/.75m3/currentCASE12/H12")
