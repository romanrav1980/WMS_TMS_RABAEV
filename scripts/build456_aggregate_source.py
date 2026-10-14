import json
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle/001_lifecycle.sql");s=p.read_text(encoding="utf-8")
old="""select count(*)into n from RRL_WMS_RECEIPT_AGG where SYSTEM_CODE=v_system and PROFILE_CODE=v_profile and CODE_HASH=v_hash and UID_PALLET=v_origin;"""
new="""select count(*)into n from(
 select a.CODE_HASH from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=u.STOCK_OPERATION_ID and op.STATE='APPLIED'
 where u.UID_PALLET=v_origin and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash
 union all
 select a.CODE_HASH from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT r on r.ORDER_ID=a.ORDER_ID and r.LINE_NUMBER=a.LINE_NUMBER
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.STOCK_OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='SAP_RECEIPT'
 where r.UID_PALLET=v_origin and r.POSTED_BASE_QTY>0 and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash
 );"""
assert s.count(old)==1;s=s.replace(old,new)
p2=Path("api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py");py=p2.read_text(encoding="utf-8")
old2='''q.execute("""select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL,''';
new2='''q.execute("""with aggregates as(
 select SYSTEM_CODE,PROFILE_CODE,CODE_HASH,AGG_LEVEL from RRL_WMS_RECEIPT_AGG where UID_PALLET=:origin
 union
 select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL from RRL_TRACE_SENDER_AGG a
 join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=u.STOCK_OPERATION_ID and op.STATE='APPLIED'
 where u.UID_PALLET=:origin
 union
 select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL from RRL_SAP_TRACE_AGG a
 join RRL_SAP_PALLET_RECEIPT r on r.ORDER_ID=a.ORDER_ID and r.LINE_NUMBER=a.LINE_NUMBER
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.STOCK_OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='SAP_RECEIPT'
 where r.UID_PALLET=:origin and r.POSTED_BASE_QTY>0)
 select a.SYSTEM_CODE,a.PROFILE_CODE,a.CODE_HASH,a.AGG_LEVEL,''';
assert py.count(old2)==1;py=py.replace(old2,new2).replace("from RRL_WMS_RECEIPT_AGG a left join","from aggregates a left join").replace("where a.UID_PALLET=:origin order by","order by")
print(json.dumps({str(p):s,str(p2):py}))
