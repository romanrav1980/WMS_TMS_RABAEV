from pathlib import Path
import json
out={}
for name in ["interwarehouse_queue.sql","interwarehouse_incoming.sql"]:
 p=Path("api/wms_api_server/app/modules/inventory/infrastructure")/name;s=p.read_text(encoding="utf-8")
 s=s.replace("p.ROOT_UID PALLET_IDENTIFIER","nvl(p.SOURCE_PLACE_UID,p.ROOT_UID)PALLET_IDENTIFIER,p.ROOT_UID STOCK_PALLET_IDENTIFIER",1)
 s=s.replace("json_value(p.SOURCE_COMPOSITION_JSON,'$.nodes[0].article')","source_leaf.ARTICLE").replace("json_value(p.SOURCE_COMPOSITION_JSON,'$.nodes[0].quantity')","source_leaf.QUANTITY").replace("json_value(p.SOURCE_COMPOSITION_JSON,'$.nodes[0].base_uom')","source_leaf.BASE_UOM")
 marker="left join RRL_INTERWARE_UNLOAD u"
 i=s.index(marker)
 join="""left join json_table(p.SOURCE_COMPOSITION_JSON,'$.nodes[*]'columns(
 UID_VALUE varchar2(200)path '$.uid',KIND_VALUE varchar2(20)path '$.kind',
 ARTICLE varchar2(160)path '$.article',QUANTITY varchar2(60)path '$.quantity',BASE_UOM varchar2(20)path '$.base_uom'))source_leaf
 on source_leaf.UID_VALUE=p.ROOT_UID and source_leaf.KIND_VALUE='STOCK'
"""
 s=s[:i]+join+s[i:]
 if name=="interwarehouse_incoming.sql":
  s=s.replace("r.ROOT_UID RECEIVED_PALLET_IDENTIFIER","case when r.OPERATION_ID is not null then nvl(p.SOURCE_PLACE_UID,r.ROOT_UID)end RECEIVED_PALLET_IDENTIFIER,r.ROOT_UID RECEIVED_STOCK_IDENTIFIER",1)
  s=s.replace("json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity')LOADED_QUANTITY","RRL_STOCK_PLAN_HELPER.decimal_text(dispatch.BASE_QTY)LOADED_QUANTITY",1)
  marker="left join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID"
  s=s.replace(marker,"""left join RRL_INTERWARE_ONWARD_DISPATCH dispatch on dispatch.OPERATION_ID=l.LOAD_OPERATION_ID
 and dispatch.BIND_OPERATION_ID=b.OPERATION_ID and dispatch.RECEIPT_OPERATION_ID=r.OPERATION_ID and dispatch.ROOT_UID=r.ROOT_UID
"""+marker,1)
 else:
  s=s.replace("r.ROOT_UID RECEIVED_PALLET_IDENTIFIER","case when r.OPERATION_ID is not null then nvl(p.SOURCE_PLACE_UID,r.ROOT_UID)end RECEIVED_PALLET_IDENTIFIER,r.ROOT_UID RECEIVED_STOCK_IDENTIFIER",1)
 out[p.as_posix()]=s
print(json.dumps(out))
