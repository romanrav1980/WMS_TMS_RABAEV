from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py");s=p.read_text(encoding="utf-8")
anchor='        params={"trip":trip_id,"addr":store_address,"actor":actor,"after_id":after,"page_size":limit}'
addition='''        try:
            with self.gateway.transaction("Current store receiver page access")as cur:
                cur.callproc("RRL_STOCK_STORE_RECEIPT_READ.require_receiver",[actor,store_address])
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)==20882:raise StoreReceiptError("STORE_RECEIPT_FORBIDDEN","Current authorized receiver required",403)from exc
            raise
'''
assert s.count(anchor)==1;s=s.replace(anchor,addition+anchor)
old="""               and (exists(select 1 from RUSERS where ID=:actor and USER_GROUP='GLOBAL_ADMIN')
                    or exists(select 1 from RRL_STORE_RECEIPT_USER where USER_ID=:actor and STORE_ADDR=:addr))"""
new="""               and exists(select 1 from RUSERS receiver where receiver.ID=:actor and nvl(receiver.DELETED,0)=0
                and RRL_HAS_WRIGHT(receiver.ID,'store_receipt_confirm')=1 and(upper(trim(receiver.USER_GROUP))='GLOBAL_ADMIN'
                    or exists(select 1 from RRL_STORE_RECEIPT_USER binding where binding.USER_ID=receiver.ID and binding.STORE_ADDR=:addr)))"""
assert s.count(old)==1;s=s.replace(old,new)
print(json.dumps({str(p):s}))
