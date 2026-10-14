from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
old='''                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:load_id,:root_id,:snapshot) from dual",
                            load_id=source_load,root_id=source[2],snapshot=source[3])'''
new='''                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(LOAD_OPERATION_ID,ROOT_UID,COMPOSITION_JSON) from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",
                            load_id=source_load)'''
assert old in s;s=s.replace(old,new)
s=s.replace("select TT_ID,WARE_ID,ROOT_UID,COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT","select TT_ID,WARE_ID,ROOT_UID from RRL_TT_HU_LOAD_FACT",1)
print(json.dumps({str(p):s},ensure_ascii=True))
