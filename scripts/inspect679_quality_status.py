exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path("tmp/context669.json").read_text())
value=OutgoingQuality(OracleGateway()).status(ctx["st_uid"],"admin")
print(json.dumps({"keys":list(value),"flags":{k:v for k,v in value.items()if isinstance(v,(bool,int,type(None)))or k in("blocking_reasons","quality_status","control_status")}},ensure_ascii=True))
Path("tmp/quality679.json").write_text(json.dumps(value),encoding="utf-8")
