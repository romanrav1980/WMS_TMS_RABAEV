exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
g=OracleGateway();qc=OutgoingQuality(g);r={}
for n in("CASE.QC.ST:4bb85f1f15:1131","CASE.QC.ST:4bb85f1f15:1132"):
 r[n]=qc.status(n,"admin")
Path("tmp/read1091_qc_current.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print(json.dumps(r,ensure_ascii=True))
