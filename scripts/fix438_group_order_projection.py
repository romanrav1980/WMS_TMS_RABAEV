from pathlib import Path
import json
p=Path('api/wms_api_server/app/modules/delivery/infrastructure/order_delivery_receipts.sql');t=p.read_text(encoding='utf-8')
needle=' where not exists(select 1 from RRL_INTERWARE_PLAN p where p.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD)'
t=t.replace(needle,needle+'\n and not exists(select 1 from RRL_IW_GROUP_PLAN p where p.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD)',1)
needle='), actual as('
addition=""" union all
 select distinct requested.ORIGINAL_LOAD,d.OPERATION_ID,d.RECEIPT_OPERATION_ID,cast(null as varchar2(100))
 from requested join RRL_IW_GROUP_DISPATCH d on d.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=d.OPERATION_ID and f.STATUS='DEPARTED'
"""+needle
assert needle in t;t=t.replace(needle,addition,1)
print(json.dumps({p.as_posix():t}))
