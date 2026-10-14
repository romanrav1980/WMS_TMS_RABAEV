from pathlib import Path
import json
s=Path("scripts/ni061_marked_source_case.py").read_text(encoding="utf-8")
s=s.replace('q.execute("select min(TRANSPORTTYPE) from RRL_TRANSPORT_TYPE");trtype=q.fetchone()[0]','trtype="15"')
# Emit actual committed source IDs after native source capture; no credentials.
s+='\nprint("SOURCE230_JSON:"+json.dumps({"tag":tag,"uid":lot,"article":article,"source_ware":ware,"target_ware":target,"source_st":st,"source_trip":trip,"target_trip":target_trip,"plan":"IW225.PLAN:"+tag,"load":shipop,"inbound":inbound,"outbound":outbound,"vehicle":vehicle,"order":order}),flush=True)\n'
print(json.dumps({"scripts/ni053_marked_disposition_source.py":s},ensure_ascii=True))
