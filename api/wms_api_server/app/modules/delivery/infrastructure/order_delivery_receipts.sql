with requested as(
 select VALUE ORIGINAL_LOAD from json_table(:loads,'$[*]'columns(VALUE varchar2(100)path '$'))
), delivery_loads as(
 select requested.ORIGINAL_LOAD,requested.ORIGINAL_LOAD FINAL_LOAD,cast(null as varchar2(100))INTERWARE_RECEIPT,
 cast(null as varchar2(100))RECOVERY_RECEIPT from requested
 where not exists(select 1 from RRL_INTERWARE_PLAN p where p.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD)
 and not exists(select 1 from RRL_IW_GROUP_PLAN p where p.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD)
 union all
 select /*+ leading(requested d f) use_nl(d f) index(d RRL_IW_DISPATCH_SOURCE_IX) */ requested.ORIGINAL_LOAD,d.OPERATION_ID,d.RECEIPT_OPERATION_ID,cast(null as varchar2(100))
 from requested join RRL_INTERWARE_ONWARD_DISPATCH d on d.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=d.OPERATION_ID and f.STATUS='DEPARTED'
 union all
 select /*+ leading(requested d f) use_nl(d f) index(d RRL_IW_REC_DISPATCH_SOURCE_IX) */ requested.ORIGINAL_LOAD,d.OPERATION_ID,d.RECEIPT_OPERATION_ID,d.RECOVERY_OPERATION_ID
 from requested join RRL_IW_RECOVERY_DISPATCH d on d.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=d.OPERATION_ID and f.STATUS='DEPARTED'
 union all
 select distinct requested.ORIGINAL_LOAD,d.OPERATION_ID,d.RECEIPT_OPERATION_ID,cast(null as varchar2(100))
 from requested join RRL_IW_GROUP_DISPATCH d on d.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=d.OPERATION_ID and f.STATUS='DEPARTED'
), actual as(
 select /*+ leading(lineage receipt line transit loss confirmed recovered recovery_op issue) use_nl(receipt line transit loss confirmed recovered recovery_op issue) */ lineage.ORIGINAL_LOAD,receipt.LOAD_OPERATION_ID FINAL_LOAD,line.LOT_UID,line.SHIPPED_BASE_QTY,line.ACCEPTED_BASE_QTY,line.MISSING_BASE_QTY,line.REFUSED_BASE_QTY,line.DAMAGED_BASE_QTY,
 receipt.OPERATION_ID RECEIPT_OPERATION,issue.STATUS CASE_STATUS,transit.ORIGINAL_ROOT_UID,transit.BASE_QTY INITIAL_QTY,
 loss.SHORT_QTY,loss.OPERATION_ID LOSS_ID,
 (select nvl(sum(found.BASE_QTY),0)from RRL_INTERWARE_RECOVERY_RECEIPT found
 join RRL_STOCK_OPERATION fo on fo.OPERATION_ID=found.OPERATION_ID and fo.STATE='APPLIED'and fo.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'
 where found.LOSS_OPERATION_ID=loss.OPERATION_ID)FOUND_QTY,
 case when confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
 and transit.ORIGINAL_ROOT_UID is not null and transit.SOURCE_LOAD_OPERATION_ID=lineage.ORIGINAL_LOAD
 and transit.BASE_QTY+loss.SHORT_QTY=transit.EXPECTED_BASE_QTY
 and((lineage.RECOVERY_RECEIPT is null and transit.ROOT_UID=line.LOT_UID and transit.BASE_QTY=line.SHIPPED_BASE_QTY)
 or(lineage.RECOVERY_RECEIPT is not null and recovered.ROOT_UID=line.LOT_UID and recovered.BASE_QTY=line.SHIPPED_BASE_QTY
 and recovered.LOSS_OPERATION_ID=loss.OPERATION_ID and recovery_op.STATE='APPLIED'and recovery_op.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'))
 then 1 else 0 end PROVEN_MAPPING,
 case when lineage.RECOVERY_RECEIPT is not null then 1 else 0 end IS_CORRECTIVE_RECEIPT
 from delivery_loads lineage join RRL_STORE_RECEIPT_FACT receipt on receipt.LOAD_OPERATION_ID=lineage.FINAL_LOAD
 join RRL_STORE_RECEIPT_LINE line on line.OPERATION_ID=receipt.OPERATION_ID
 left join RRL_INTERWARE_RECEIPT transit on transit.OPERATION_ID=lineage.INTERWARE_RECEIPT
 left join RRL_INTERWARE_SHORTAGE_FACT loss on loss.RECEIPT_OPERATION_ID=transit.OPERATION_ID
 left join RRL_STOCK_OPERATION confirmed on confirmed.OPERATION_ID=loss.OPERATION_ID
 left join RRL_INTERWARE_RECOVERY_RECEIPT recovered on recovered.OPERATION_ID=lineage.RECOVERY_RECEIPT
 left join RRL_STOCK_OPERATION recovery_op on recovery_op.OPERATION_ID=recovered.OPERATION_ID
 left join RRL_STORE_DISCREPANCY_CASE issue on issue.CASE_ID=receipt.OPERATION_ID
)
select ORIGINAL_LOAD LOAD_OPERATION_ID,FINAL_LOAD ACTUAL_FINAL_LOAD_OPERATION_ID,LOT_UID,
 case when PROVEN_MAPPING=1 then ORIGINAL_ROOT_UID else LOT_UID end ORIGINAL_LOT_UID,
 RRL_STOCK_PLAN_HELPER.decimal_text(case when PROVEN_MAPPING=1 then SHORT_QTY else 0 end)CONFIRMED_TRANSPORT_SHORTAGE,
 case when PROVEN_MAPPING=1 then LOSS_ID else null end TRANSPORT_SHORTAGE_OPERATION_ID,
 RRL_STOCK_PLAN_HELPER.decimal_text(case when PROVEN_MAPPING=1 then nvl(FOUND_QTY,0)else 0 end)RECOVERED_TRANSPORT_QUANTITY,
 RRL_STOCK_PLAN_HELPER.decimal_text(case when PROVEN_MAPPING=1 then INITIAL_QTY else SHIPPED_BASE_QTY end)INITIAL_SHIPPED_QUANTITY,
 IS_CORRECTIVE_RECEIPT,RECEIPT_OPERATION,CASE_STATUS,
 RRL_STOCK_PLAN_HELPER.decimal_text(SHIPPED_BASE_QTY)SHIPPED,RRL_STOCK_PLAN_HELPER.decimal_text(ACCEPTED_BASE_QTY)ACCEPTED,
 RRL_STOCK_PLAN_HELPER.decimal_text(MISSING_BASE_QTY)MISSING,RRL_STOCK_PLAN_HELPER.decimal_text(REFUSED_BASE_QTY)REFUSED,
 RRL_STOCK_PLAN_HELPER.decimal_text(DAMAGED_BASE_QTY)DAMAGED
from actual fetch first 2001 rows only
