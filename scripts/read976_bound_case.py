exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
ctx=json.loads(Path("tmp/context975.json").read_text(encoding="utf-8"));assert ctx["stage"]=="MOVED"
result=OutgoingQuality(OracleGateway()).status(ctx["st"],"admin")
assert result["case_content_version"]==3 and result["composition_signature"]==ctx["before_qc"]["composition_signature"]
ctx["after_qc"]=result;ctx["qc_interpretation"]="Same goods composition hash is correct for whole-place relocation; case physical version advances. No pre-existing QC approval invalidation was tested."
ctx["final_harness_correction"]="975 final expected changed quantity hash was incorrect; stock/CT/FF/rollback/replay/facts assertions passed before it"
Path("tmp/context975.json").write_text(json.dumps(ctx,indent=2,default=str),encoding="utf-8")
print("PASS976 original CASE/FF3 physical12/H12 and originalfacts proof retained; currentQC version3, unchanged goods composition hash; no false old-approval invalidation claim")
