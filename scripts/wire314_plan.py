from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
needle='                result = {"operation_id":operation_id,"status":"PLANNED"'
i=s.index(needle)
s=s[:i]+'''                stock_uid=cur.callfunc("RRL_IW_HU_SOURCE.stock_uid",str,[source_load])
                hu_wire=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_IW_HU_SOURCE.capture_context",[source_load,actor,hu_wire])
                source_hu=read_oracle_json(hu_wire.getvalue())if hu_wire.getvalue()is not None else None
'''+s[i:]
needle='                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(LOAD_OPERATION_ID,ROOT_UID,COMPOSITION_JSON) from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",\n                            load_id=source_load)'
assert needle in s
s=s.replace(needle,'''                if source_hu:
                    result.update(stock_pallet_identifier=stock_uid,physical_tree_expected=True,physical_place_identifier=source[2])
                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(LOAD_OPERATION_ID,:stock_uid,COMPOSITION_JSON) from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",
                            stock_uid=stock_uid,load_id=source_load)''',1)
s=s.replace('cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB,arrival=','cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB,source_hu=oracledb.DB_TYPE_CLOB,arrival=',1)
s=s.replace('TARGET_TT_ID,ROOT_UID,SOURCE_COMPOSITION_JSON,INBOUND_DOCK','TARGET_TT_ID,ROOT_UID,SOURCE_PLACE_UID,SOURCE_HU_JSON,SOURCE_COMPOSITION_JSON,INBOUND_DOCK',1)
s=s.replace(':ware,:trip,f.ROOT_UID,f.COMPOSITION_JSON,:inbound',':ware,:trip,:stock_uid,:source_place,:source_hu,f.COMPOSITION_JSON,:inbound',1)
s=s.replace('op=operation_id,digest=digest,st=members[0][0],ware=target_ware','stock_uid=stock_uid,source_place=source[2]if source_hu else None,source_hu=json.dumps(source_hu)if source_hu else None,op=operation_id,digest=digest,st=members[0][0],ware=target_ware',1)
print(json.dumps({p.as_posix():s}))
