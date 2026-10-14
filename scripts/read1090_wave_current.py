exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.wave_execution import WaveExecution
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
g=OracleGateway();r=WaveExecution(g).preview(553,"admin");hu=WarehouseHu(g)
roots=[hu.preview(n,"admin")for n in("HU1069:4bb85f1f15","HU994:4bb85f1f15")]
Path("tmp/read1090_wave_current.json").write_text(json.dumps({"wave":r,"roots":roots},indent=2,default=str),encoding="utf-8")
print(json.dumps(r,ensure_ascii=True))
print("CURRENTVERSIONS",[(x["root"],[(n["uid"],n.get("version"),n.get("cell"))for n in x["nodes"]])for x in roots])
